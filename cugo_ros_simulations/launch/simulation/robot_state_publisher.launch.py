import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():

    # ========== 수정: 기본값 false → true ==========
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')  # 변경됨

    package_dir = get_package_share_directory("cugo_ros2_control")
    urdf = os.path.join(package_dir, "models", "cugo_v3", "cugo_v3.urdf")
    
    # ========== 추가: URDF 파일 내용 읽기 ==========
    with open(urdf, 'r') as infp:
        robot_description = infp.read()

    return LaunchDescription([
        DeclareLaunchArgument(
            'use_sim_time',
            # ========== 수정: 기본값 false → true ==========
            default_value='true',  # 변경됨
            description='Use simulation (Gazebo) clock if true'),

        Node(
            package='robot_state_publisher',
            executable='robot_state_publisher',
            name='robot_state_publisher',
            output='screen',
            # ========== 수정: arguments → parameters 방식 변경 ==========
            parameters=[{
                'use_sim_time': use_sim_time,
                'robot_description': robot_description  # 추가됨
            }],
            # arguments=[urdf]  # 삭제됨
        ),
    ])