#!/usr/bin/env python3
"""
Pointcloud to LaserScan Conversion Launch File
Converts Ouster 3D LiDAR PointCloud2 data to 2D LaserScan for SLAM and Navigation
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
    
    # Path to config file
    config_file = os.path.join(
        pkg_dir,
        'config',
        'laser_filters',
        'pointcloud_to_laserscan.yaml'
    )
    
    # Declare launch arguments
    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )
    
    # Pointcloud to LaserScan node
    pointcloud_to_laserscan_node = Node(
        package='pointcloud_to_laserscan',
        executable='pointcloud_to_laserscan_node',
        name='pointcloud_to_laserscan',
        output='screen',
        parameters=[
            config_file,
            {'use_sim_time': LaunchConfiguration('use_sim_time')}
        ],
        remappings=[
            # Input: Ouster publishes to /ouster/points as PointCloud2
            ('cloud_in', '/ouster/points'),
            # Output: Standard 2D laser scan topic
            ('scan', '/scan')
        ]
    )
    
    return LaunchDescription([
        use_sim_time_arg,
        pointcloud_to_laserscan_node,
    ])

