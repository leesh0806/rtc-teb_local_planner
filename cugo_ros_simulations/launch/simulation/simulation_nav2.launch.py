import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    package_dir = get_package_share_directory('cugo_ros2_control')

    # 기본 맵 경로
    # 소스 디렉토리 경로 계산 (launch 파일 위치 기준)
    launch_file_dir = os.path.dirname(os.path.abspath(__file__))
    source_dir = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(launch_file_dir))),
        'cugo_ros_simulations')
    
    source_map_path = os.path.join(source_dir, 'worlds', 'map', 'my_map.yaml')
    installed_map_path = os.path.join(package_dir, 'worlds', 'map', 'my_map.yaml')
    
    # map 파일이 존재하는 경로 선택 (소스 디렉토리 우선)
    if os.path.exists(source_map_path):
        default_map_path = source_map_path
    elif os.path.exists(installed_map_path):
        default_map_path = installed_map_path
    else:
        # map 파일이 없으면 설치된 경로 사용 (경고는 nav2_bringup에서 처리)
        default_map_path = installed_map_path
    
    # 기본 파라미터 파일 경로
    default_params_path = os.path.join(
        package_dir, 
        'config', 'simulation', 'cugo_v3.yaml')

    # LaunchConfiguration 선언
    map_yaml_file = LaunchConfiguration('map')
    params_file = LaunchConfiguration('params_file')
    use_sim_time = LaunchConfiguration('use_sim_time')
    autostart = LaunchConfiguration('autostart')
    slam = LaunchConfiguration('slam')

    nav2_launch_file_dir = os.path.join(get_package_share_directory('nav2_bringup'), 'launch')
    rviz_config_dir = os.path.join(package_dir, 'rviz', 'nav2_default_view.rviz')

    return LaunchDescription([
        # Declare launch arguments
        DeclareLaunchArgument(
            'map',
            default_value=default_map_path,
            description='Full path to map yaml file to load'),

        DeclareLaunchArgument(
            'params_file',
            default_value=default_params_path,
            description='Full path to the ROS2 parameters file to use'),

        DeclareLaunchArgument(
            'use_sim_time',
            default_value='true',
            description='Use simulation (Gazebo) clock if true'),

        DeclareLaunchArgument(
            'autostart',
            default_value='true',
            description='Automatically startup the nav2 stack'),

        DeclareLaunchArgument(
            'slam',
            default_value='False',
            description='Whether to run SLAM (False = use map_server with pre-built map)'),

        # Nav2 bringup
        IncludeLaunchDescription(
            PythonLaunchDescriptionSource(
                os.path.join(nav2_launch_file_dir, 'bringup_launch.py')),
            launch_arguments={
                'map': map_yaml_file,
                'use_sim_time': use_sim_time,
                'params_file': params_file,
                'autostart': autostart,
                'slam': slam,
            }.items(),
        ),

        # RViz2
        Node(
            package='rviz2',
            executable='rviz2',
            name='rviz2',
            arguments=['-d', rviz_config_dir],
            parameters=[{'use_sim_time': use_sim_time}],
            output='screen'),
    ])
