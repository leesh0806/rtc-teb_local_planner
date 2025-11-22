#!/usr/bin/env python3

import os
from ament_index_python.packages import get_package_share_directory
import subprocess
import sys

def main():
    package_dir = get_package_share_directory('cugo_ros2_control')
    config_file = os.path.join(package_dir, 'config', 'laser_filters', 'v3ros_filter.yaml')
    
    if not os.path.exists(config_file):
        print(f'[ERROR] 설정 파일을 찾을 수 없습니다: {config_file}')
        sys.exit(1)
    
    print(f'[INFO] LiDAR Scan Filter 시작...')
    print(f'[INFO] 설정 파일: {config_file}')
    print(f'[INFO] 입력 토픽: /scan')
    print(f'[INFO] 출력 토픽: /scan_filtered')
    print('[INFO] 필터 적용 중:')
    print('  - 로봇 몸체 영역 제거 (Box Filter)')
    print('  - 알루미늄 프레임 영역 제거 (각도별 필터)')
    
    # laser_filters 노드 실행
    try:
        subprocess.run([
            'ros2', 'run', 'laser_filters', 'scan_to_scan_filter_chain',
            '--ros-args',
            '--params-file', config_file,
            '-r', 'scan:=/scan',
            '-r', 'scan_filtered:=/scan_filtered',
            '-p', 'use_sim_time:=true'
        ])
    except KeyboardInterrupt:
        print('\n[INFO] LiDAR Filter 종료')

if __name__ == '__main__':
    main()