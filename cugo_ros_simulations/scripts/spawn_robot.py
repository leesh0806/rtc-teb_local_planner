#!/usr/bin/env python3

import os
import sys
import subprocess
from ament_index_python.packages import get_package_share_directory

def main():
    if len(sys.argv) < 2:
        print("사용법:")
        print("  기본 위치: ros2 run cugo_ros2_control spawn_robot.py default")
        print("  커스텀:   ros2 run cugo_ros2_control spawn_robot.py x y z yaw")
        print("\n예시:")
        print("  ros2 run cugo_ros2_control spawn_robot.py default")
        print("  ros2 run cugo_ros2_control spawn_robot.py 1.0 2.0 0.2 1.57")
        sys.exit(1)
    
    # 기본값
    x, y, z, yaw = '0.0', '0.0', '0.2', '0.0'
    
    if sys.argv[1] != 'default':
        if len(sys.argv) < 5:
            print("[ERROR] 4개의 값이 필요합니다: x y z yaw")
            sys.exit(1)
        x, y, z, yaw = sys.argv[1:5]
    
    package_dir = get_package_share_directory('cugo_ros2_control')
    urdf_file = os.path.join(package_dir, 'models', 'cugo_v3', 'cugo_v3.urdf')
    
    print(f'[INFO] 로봇 Spawn 중...')
    print(f'[INFO] URDF: {urdf_file}')
    print(f'[INFO] 위치: x={x}, y={y}, z={z}, yaw={yaw}')
    
    # 로봇 생성
    result = subprocess.run([
        'ros2', 'run', 'ros_gz_sim', 'create',
        '-name', 'cugo_v3',
        '-file', urdf_file,
        '-x', x,
        '-y', y,
        '-z', z,
        '-Y', yaw
    ])
    
    if result.returncode == 0:
        print('[INFO] ✅ 로봇이 성공적으로 생성되었습니다!')
    else:
        print('[ERROR] ❌ 로봇 생성 실패!')
        sys.exit(1)

if __name__ == '__main__':
    main()