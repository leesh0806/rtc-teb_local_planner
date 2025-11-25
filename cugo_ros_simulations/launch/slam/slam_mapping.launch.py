#!/usr/bin/env python3
"""
SLAM Toolbox Mapping Launch File for CuGo V3 Robot
Creates 2D occupancy grid map from LaserScan data
"""

from launch import LaunchDescription
from launch_ros.actions import Node
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
import os


def generate_launch_description():
    # Get package directory
    pkg_dir = get_package_share_directory('cugo_ros2_control')
    
    # Path to SLAM config file
    slam_params_file = os.path.join(
        pkg_dir,
        'config',
        'slam',
        'slam_toolbox_params.yaml'
    )
    
    # Declare launch arguments
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )
    
    slam_params_arg = DeclareLaunchArgument(
        'slam_params_file',
        default_value=slam_params_file,
        description='Path to SLAM Toolbox parameters file'
    )
    
    # SLAM Toolbox Node (Async mode for real-time mapping)
    slam_toolbox_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[
            LaunchConfiguration('slam_params_file'),
            {'use_sim_time': LaunchConfiguration('use_sim_time')}
        ],
        # Remap scan topic QoS to match pointcloud_to_laserscan (BEST_EFFORT)
        arguments=['--ros-args', '--log-level', 'info'],
    )
    
    return LaunchDescription([
        use_sim_time_arg,
        slam_params_arg,
        slam_toolbox_node,
    ])

