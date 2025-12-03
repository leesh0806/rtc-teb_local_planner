#!/usr/bin/env python3
"""
통합 웨이포인트 네비게이터
TEB/MPPI 플래너 비교 실험용

사용법:
    ros2 run cugo_ros2_control waypoint_navigator.py --scenario <scenario_name>
    
    사용 가능한 시나리오는 waypoint_definitions.py에서 확인할 수 있습니다.
"""
import rclpy
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from geometry_msgs.msg import PoseStamped
import math
import time
import argparse
import sys
import os
import subprocess
from pathlib import Path

# waypoint_definitions.py를 같은 디렉토리에서 import하기 위한 경로 설정
script_dir = os.path.dirname(os.path.abspath(__file__))
if script_dir not in sys.path:
    sys.path.insert(0, script_dir)

from waypoint_definitions import get_waypoint_list, SCENARIOS


class WaypointNavigator:
    def __init__(self, scenario_name, record_bag=False, bag_output_dir=None, planner_type=None):
        rclpy.init()
        self.nav = BasicNavigator()
        self.scenario_name = scenario_name
        self.record_bag = record_bag
        self.bag_output_dir = bag_output_dir
        self.planner_type = planner_type
        self.bag_process = None
        
        print(f"\n{'='*60}")
        print(f"🚀 Waypoint Navigator - {scenario_name.upper()} Scenario")
        print(f"{'='*60}\n")
        print("⏳ Waiting for Nav2 to be ready...")
        
        self.nav.waitUntilNav2Active()
        print("✅ Nav2 is ready!\n")
        
        # rosbag 기록 시작
        if self.record_bag:
            self.start_rosbag_recording()
    
    def start_rosbag_recording(self):
        """ros2 bag record 서브프로세스 시작"""
        # 기본 토픽 세트
        topics = [
            "/imu/data_raw",
            "/odom",
            "/cmd_vel",
            "/amcl_pose",
            "/tf",
            "/tf_static",
        ]
        
        # 플래너별 추가 토픽
        if self.planner_type == "teb":
            topics.extend(["/local_plan", "/global_plan"])
        elif self.planner_type == "mppi":
            # MPPI는 /local_plan 대신 다른 토픽 사용
            topics.extend(["/plan", "/transformed_global_plan"])
        else:
            # 플래너 미지정 시 모든 plan 토픽 시도
            topics.extend(["/local_plan", "/global_plan", "/plan", "/transformed_global_plan"])
        
        # bag 출력 디렉토리 설정
        if self.bag_output_dir:
            bag_dir = Path(self.bag_output_dir).expanduser().resolve()
        else:
            # 기본값: evaluation/rosbags/<planner_type>/
            # 소스 디렉토리 찾기 (install 디렉토리에서 실행될 수도 있음)
            script_path = Path(__file__).resolve()
            
            # install 디렉토리인 경우 소스 디렉토리로 변환
            if 'install' in script_path.parts:
                # install/cugo_ros2_control/lib/cugo_ros2_control/evaluation/scenarios/waypoint_navigator.py
                # -> src/rtc-teb_local_planner/cugo_ros_simulations/evaluation/rosbags/
                install_idx = script_path.parts.index('install')
                workspace_root = Path(*script_path.parts[:install_idx])
                eval_dir = workspace_root / "src" / "rtc-teb_local_planner" / "cugo_ros_simulations" / "evaluation"
            else:
                # 소스 디렉토리에서 직접 실행
                script_dir = script_path.parent  # evaluation/scenarios/
                eval_dir = script_dir.parent     # evaluation/
            
            planner = self.planner_type or "default"
            bag_dir = eval_dir / "rosbags" / planner
        
        bag_dir.mkdir(parents=True, exist_ok=True)
        
        # bag 파일 이름: <scenario>_<timestamp>
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        bag_name = f"{self.scenario_name}_{timestamp}"
        
        cmd = ["ros2", "bag", "record"] + topics + ["-o", bag_name]
        
        print(f"🎥 Starting rosbag recording...")
        print(f"   Directory: {bag_dir}")
        print(f"   Bag name: {bag_name}")
        print(f"   Topics: {', '.join(topics)}\n")
        
        self.bag_process = subprocess.Popen(
            cmd,
            cwd=str(bag_dir),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        
        # rosbag이 시작될 시간을 주기 위해 짧은 대기
        time.sleep(2)
    
    def stop_rosbag_recording(self):
        """ros2 bag record 서브프로세스 종료"""
        if self.bag_process is None:
            return
        
        if self.bag_process.poll() is not None:
            # 이미 종료됨
            return
        
        print("\n🛑 Stopping rosbag recording...")
        self.bag_process.terminate()
        
        try:
            self.bag_process.wait(timeout=10.0)
            print("✅ Rosbag recording stopped successfully.\n")
        except subprocess.TimeoutExpired:
            print("⚠️  Rosbag process did not exit in time. Forcing kill...")
            self.bag_process.kill()
            self.bag_process.wait()
        
        self.bag_process = None
        
    def create_pose(self, x, y, yaw_deg):
        """PoseStamped 메시지 생성 (각도는 degree)"""
        yaw_rad = math.radians(yaw_deg)
        q_z = math.sin(yaw_rad / 2.0)
        q_w = math.cos(yaw_rad / 2.0)
        
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.header.stamp = self.nav.get_clock().now().to_msg()
        pose.pose.position.x = x
        pose.pose.position.y = y
        pose.pose.position.z = 0.0
        pose.pose.orientation.x = 0.0
        pose.pose.orientation.y = 0.0
        pose.pose.orientation.z = q_z
        pose.pose.orientation.w = q_w
        return pose
    
    def get_waypoints(self, scenario):
        """
        시나리오별 웨이포인트 반환
        
        waypoint_definitions.py에서 정의된 시나리오를 사용합니다.
        """
        # waypoint_definitions.py에서 웨이포인트 좌표 가져오기
        if scenario not in SCENARIOS:
            raise ValueError(
                f"Unknown scenario '{scenario}'. "
                f"Available scenarios: {', '.join(SCENARIOS.keys())}"
            )
        
        coords = get_waypoint_list(scenario)
        return [self.create_pose(x, y, yaw) for x, y, yaw in coords]
    
    def run_experiment(self):
        """실험 실행 및 결과 반환"""
        waypoints = self.get_waypoints(self.scenario_name)
        
        print(f"📍 Waypoints: {len(waypoints)} points")
        for i, wp in enumerate(waypoints, 1):
            x = wp.pose.position.x
            y = wp.pose.position.y
            # yaw 계산
            q_z = wp.pose.orientation.z
            q_w = wp.pose.orientation.w
            yaw_rad = 2 * math.atan2(q_z, q_w)
            yaw_deg = math.degrees(yaw_rad)
            print(f"  {i}. x={x:6.2f}, y={y:6.2f}, yaw={yaw_deg:7.1f}°")
        
        print(f"\n{'='*60}")
        print("🏁 Starting navigation...")
        print(f"{'='*60}\n")
        
        self.nav.followWaypoints(waypoints)
        
        # 피드백 출력
        start_time = time.time()
        last_waypoint = -1
        
        while not self.nav.isTaskComplete():
            feedback = self.nav.getFeedback()
            if feedback:
                current = feedback.current_waypoint + 1
                total = len(waypoints)
                elapsed = time.time() - start_time
                
                # 새로운 웨이포인트로 이동했을 때만 출력
                if current != last_waypoint:
                    print(f"⏱️  Progress: {current}/{total} waypoints "
                          f"(Elapsed: {elapsed:.1f}s)")
                    last_waypoint = current
            
            rclpy.spin_once(self.nav, timeout_sec=1.0)
            
            # 타임아웃 (10분)
            if time.time() - start_time > 600:
                print("\n⚠️  Timeout! Canceling navigation...")
                self.nav.cancelTask()
                break
        
        # 결과 확인
        result = self.nav.getResult()
        total_time = time.time() - start_time
        
        # rosbag 정리
        if self.record_bag:
            self.stop_rosbag_recording()
        
        print(f"\n{'='*60}")
        if result == TaskResult.SUCCEEDED:
            print(f"✅ SUCCESS! Completed in {total_time:.1f}s")
            print(f"{'='*60}\n")
            return True
        elif result == TaskResult.CANCELED:
            print(f"⚠️  CANCELED after {total_time:.1f}s")
            print(f"{'='*60}\n")
            return False
        elif result == TaskResult.FAILED:
            print(f"❌ FAILED after {total_time:.1f}s")
            print(f"{'='*60}\n")
            return False
        else:
            print(f"❓ Unknown result: {result}")
            print(f"{'='*60}\n")
            return False
    
    def shutdown(self):
        """노드 종료 (Nav2는 계속 실행 상태 유지)"""
        # rosbag가 아직 살아 있으면 정리
        if self.record_bag:
            self.stop_rosbag_recording()
        
        # lifecycleShutdown()을 호출하면 Nav2 전체가 종료되므로 제거
        # Nav2는 계속 실행 상태로 두고, 이 스크립트만 종료
        rclpy.shutdown()


def main():
    parser = argparse.ArgumentParser(
        description='Waypoint Navigator for TEB/MPPI Comparison Experiments',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  ros2 run cugo_ros2_control waypoint_navigator.py --scenario <scenario_name>
  
Note: --scenario option is required. Available scenarios: {scenarios}
        """.format(scenarios=', '.join(SCENARIOS.keys()))
    )
    parser.add_argument(
        '--scenario', 
        required=True,
        choices=list(SCENARIOS.keys()),
        help='Experiment scenario to run (required)'
    )
    parser.add_argument(
        '--record-bag',
        action='store_true',
        help='Enable rosbag recording during navigation'
    )
    parser.add_argument(
        '--bag-dir',
        type=str,
        default=None,
        help='Directory to save rosbag files (default: evaluation/rosbags/<planner>/)'
    )
    parser.add_argument(
        '--planner',
        type=str,
        choices=['teb', 'mppi'],
        default=None,
        help='Planner type (teb or mppi) - used for default bag directory naming'
    )
    args = parser.parse_args()
    
    navigator = WaypointNavigator(
        scenario_name=args.scenario,
        record_bag=args.record_bag,
        bag_output_dir=args.bag_dir,
        planner_type=args.planner,
    )
    try:
        success = navigator.run_experiment()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Shutting down...")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        navigator.shutdown()


if __name__ == '__main__':
    main()

