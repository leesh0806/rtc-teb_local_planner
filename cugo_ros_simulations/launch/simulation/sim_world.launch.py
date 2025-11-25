import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, ExecuteProcess, SetEnvironmentVariable, TimerAction, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node

def generate_launch_description():
    # ========== Launch Arguments ==========
    declare_world_arg = DeclareLaunchArgument(
        'world',
        default_value='cugo_v3_world',
        description='월드 선택: cugo_v3_world (평지) 또는 rubicon (산악)',
        choices=['cugo_v3_world', 'rubicon', 'tugbot_depot']
    )
    
    declare_x_arg = DeclareLaunchArgument(
        'x', default_value='0.0',
        description='로봇 spawn X 좌표 (m)'
    )
    
    declare_y_arg = DeclareLaunchArgument(
        'y', default_value='0.0',
        description='로봇 spawn Y 좌표 (m)'
    )
    
    declare_z_arg = DeclareLaunchArgument(
        'z', default_value='0.2',
        description='로봇 spawn Z 좌표 (높이, m)'
    )
    
    declare_yaw_arg = DeclareLaunchArgument(
        'yaw', default_value='0.0',
        description='로봇 spawn 방향 (라디안)'
    )
    
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    world_name = LaunchConfiguration('world')
    spawn_x = LaunchConfiguration('x')
    spawn_y = LaunchConfiguration('y')
    spawn_z = LaunchConfiguration('z')
    spawn_yaw = LaunchConfiguration('yaw')

    package_dir = get_package_share_directory('cugo_ros2_control')
    launch_file_dir = os.path.join(package_dir, 'launch', 'simulation')
    
    # Sensor description 패키지 경로 추가
    sensors_dir = get_package_share_directory('clearpath_sensors_description')

    # World 파일 경로 생성
    world_path = PathJoinSubstitution([
        package_dir, 'worlds', 'sim_worlds', 
        [world_name, '.sdf']
    ])
    
    # URDF 파일 경로
    urdf_file = os.path.join(package_dir, 'models', 'cugo_v3', 'cugo_v3.urdf')
    
    print('urdf path: ', urdf_file)

    # ========== Ignition Gazebo 리소스 경로 설정 ==========
    # clearpath_sensors_description 패키지 경로를 추가하여 mesh 파일을 찾을 수 있도록 함
    resource_paths = f"{package_dir}:{sensors_dir}"
    
    # ROS share 디렉토리를 추가하여 모든 ROS 패키지의 리소스를 찾을 수 있도록 함
    ros_share_path = "/opt/ros/humble/share"
    
    ign_resource_path = SetEnvironmentVariable(
        name='IGN_GAZEBO_RESOURCE_PATH',
        value=resource_paths
    )
    
    gz_resource_path = SetEnvironmentVariable(
        name='GZ_SIM_RESOURCE_PATH', 
        value=resource_paths
    )
    
    # IGN_FILE_PATH 설정 - Gazebo가 package:// URI를 해석할 수 있도록 함
    ign_file_path = SetEnvironmentVariable(
        name='IGN_FILE_PATH',
        value=ros_share_path
    )

    # Gazebo 실행 (GUI 툴바 표시를 위해 -r 플래그 제거)
    # -r 플래그는 시뮬레이션을 즉시 실행하지만 GUI 초기화를 방해할 수 있음
    gazebo = ExecuteProcess(
        cmd=['ign', 'gazebo', world_path],
        output='screen'
    )

    # Robot State Publisher
    robot_state_publisher = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(launch_file_dir, 'robot_state_publisher.launch.py')
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items(),
    )

    # ========== ROS-Gazebo Bridge ==========
    # Bridges Ignition topics to ROS2 topics
    # 두 월드 모두 지원하기 위해 양쪽 joint_state 토픽을 모두 브릿지
    bridge = Node(
        package='ros_gz_bridge',
        executable='parameter_bridge',
        arguments=[
            '/clock@rosgraph_msgs/msg/Clock[ignition.msgs.Clock',
            '/cmd_vel@geometry_msgs/msg/Twist@ignition.msgs.Twist',
            '/odom@nav_msgs/msg/Odometry@ignition.msgs.Odometry',
            '/sensors/ouster/scan/points@sensor_msgs/msg/PointCloud2[ignition.msgs.PointCloudPacked',  # ← 3D LiDAR
            '/world/cugo_world/model/cugo_v3/joint_state@sensor_msgs/msg/JointState[ignition.msgs.Model',  # ← cugo_v3_world
            '/world/rubicon/model/cugo_v3/joint_state@sensor_msgs/msg/JointState[ignition.msgs.Model',  # ← rubicon world
            '/world/world_demo/model/cugo_v3/joint_state@sensor_msgs/msg/JointState[ignition.msgs.Model',
            '/imu@sensor_msgs/msg/Imu[ignition.msgs.IMU',  # ← IMU
        ],
        remappings=[
            ('/world/cugo_world/model/cugo_v3/joint_state', '/joint_states'),  # ← cugo_v3_world
            ('/world/rubicon/model/cugo_v3/joint_state', '/joint_states'),  # ← rubicon world (같은 ROS 토픽으로 매핑)
            ('/world/world_demo/model/cugo_v3/joint_state', '/joint_states'),  # ← world_demo world (같은 ROS 토픽으로 매핑)
            ('/imu', '/imu/data_raw'),  # ← IMU remapping
            ('/sensors/ouster/scan/points', '/ouster/points'),  # ← 3D LiDAR remapping
        ],
        output='screen'
    )

    # 로봇 Spawn (Gazebo 월드 로딩 대기)
    spawn_robot = TimerAction(
        period=5.0,  # 기본 5초 대기 (Rubicon은 첫 실행 시 더 오래 걸릴 수 있음)
        actions=[
            Node(
                package='ros_gz_sim',
                executable='create',
                arguments=[
                    '-name', 'cugo_v3',
                    '-file', urdf_file,
                    '-x', spawn_x,
                    '-y', spawn_y,
                    '-z', spawn_z,
                    '-Y', spawn_yaw,
                ],
                output='screen'
            )
        ]
    )

    # ========== Odom TF Publisher ==========
    # Gazebo의 /odom 토픽을 받아서 odom → base_footprint TF를 발행
    odom_tf_publisher = Node(
        package='cugo_ros2_control',
        executable='odom_tf_publisher.py',
        name='odom_tf_publisher',
        parameters=[
            {'odom_topic': '/odom'},
            {'odom_frame': 'odom'},
            {'base_frame': 'base_footprint'},
            {'use_sim_time': use_sim_time}
        ],
        output='screen'
    )

    return LaunchDescription([
        # Launch Arguments
        declare_world_arg,
        declare_x_arg,
        declare_y_arg,
        declare_z_arg,
        declare_yaw_arg,
        # Environment Variables
        ign_resource_path,
        gz_resource_path,
        ign_file_path,
        # Nodes and Processes
        gazebo,
        robot_state_publisher,
        bridge,
        spawn_robot,
        odom_tf_publisher,
    ])