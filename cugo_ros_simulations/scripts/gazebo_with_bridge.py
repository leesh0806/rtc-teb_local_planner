#!/usr/bin/env python3

import os
import sys
import subprocess
import signal
from ament_index_python.packages import get_package_share_directory

def signal_handler(sig, frame):
    """Ctrl+C 処理"""
    print('\n終了中...')
    sys.exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)
    
    package_dir = get_package_share_directory('cugo_ros2_control')
    
    # 環境変数 設定
    env = os.environ.copy()
    env['IGN_GAZEBO_RESOURCE_PATH'] = package_dir
    env['GZ_SIM_RESOURCE_PATH'] = package_dir
    
    # World ファイル パス
    world_file = os.path.join(package_dir, 'worlds', 'sim_worlds', 'cugo_v3_world.sdf')
    
    print(f'[INFO] Gazebo World 実行: {world_file}')
    print(f'[INFO] リソース パス: {package_dir}')
    
    # Gazebo プロセス 始まり
    gazebo_process = subprocess.Popen(
        ['ign', 'gazebo', world_file, '-r'],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    print('[INFO] Gazebo 始まり完了. 5秒お待ち...')
    import time
    time.sleep(5)  # Gazeboが完全に起動するまで待ちます
    
    # ROS-Gazebo Bridge 始まり
    print('[INFO] ROS-Gazebo Bridge 始まり...')
    bridge_process = subprocess.Popen([
        'ros2', 'run', 'ros_gz_bridge', 'parameter_bridge',
        '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock',
        '/cmd_vel@geometry_msgs/msg/Twist@ignition.msgs.Twist',
        '/odom@nav_msgs/msg/Odometry@ignition.msgs.Odometry',
        '/scan@sensor_msgs/msg/LaserScan@ignition.msgs.LaserScan',
        '/world/cugo_world/model/cugo_v3/joint_state@sensor_msgs/msg/JointState[ignition.msgs.Model',
        '/imu@sensor_msgs/msg/Imu[ignition.msgs.IMU',  # ← IMU bridge
        '--ros-args',
        '-r', '/world/cugo_world/model/cugo_v3/joint_state:=/joint_states',
        '-r', '/imu:=/imu/data_raw'  # ← IMU를 /imu/data_raw로 remapping
    ])
    
    print('[INFO] ✅ Gazebo WorldとBridgeが実行中です.')
    print('[INFO] 終了するには Ctrl+C を押してください.')
    
    try:
        # 2つのプロセスが終了するまで待ちます
        gazebo_process.wait()
        bridge_process.wait()
    except KeyboardInterrupt:
        print('\n[INFO] 終了信号を受信. プロセス終了中...')
        gazebo_process.terminate()
        bridge_process.terminate()
        gazebo_process.wait()
        bridge_process.wait()

if __name__ == '__main__':
    main()