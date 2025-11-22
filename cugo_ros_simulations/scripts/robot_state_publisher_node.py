#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
import rclpy
from rclpy.node import Node

def main():
    # ROS2 초기화
    rclpy.init()
    
    # 패키지 경로 가져오기
    package_dir = get_package_share_directory('cugo_ros2_control')
    urdf_file = os.path.join(package_dir, 'models', 'cugo_v3', 'cugo_v3.urdf')
    
    # URDF 파일 읽기
    with open(urdf_file, 'r') as f:
        robot_description = f.read()
    
    print(f'[INFO] URDF 파일 로드: {urdf_file}')
    print(f'[INFO] URDF 크기: {len(robot_description)} bytes')
    
    # robot_state_publisher 실행
    import subprocess
    
    # 임시 파라미터 파일 생성
    import tempfile
    import yaml
    
    param_dict = {
        'robot_state_publisher': {
            'ros__parameters': {
                'use_sim_time': True,
                'robot_description': robot_description
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(param_dict, f)
        param_file = f.name
    
    print(f'[INFO] Robot State Publisher 시작...')
    
    try:
        # robot_state_publisher 실행
        subprocess.run([
            'ros2', 'run', 'robot_state_publisher', 'robot_state_publisher',
            '--ros-args',
            '--params-file', param_file
        ])
    finally:
        # 임시 파일 삭제
        os.unlink(param_file)
    
    rclpy.shutdown()

if __name__ == '__main__':
    main()