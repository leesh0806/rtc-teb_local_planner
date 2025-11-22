#!/usr/bin/env python3

"""
Odometry TF Publisher Node

Gazebo Fortress의 DiffDrive 플러그인은 /odom 토픽은 발행하지만
odom → base_footprint TF를 발행하지 않습니다.

이 노드는:
1. /odom 토픽을 구독
2. odom → base_footprint TF를 발행
3. IMU 데이터가 제대로 작동하도록 TF tree를 완성
"""

import rclpy
from rclpy.node import Node
from nav_msgs.msg import Odometry
from geometry_msgs.msg import TransformStamped
from tf2_ros import TransformBroadcaster


class OdomTFPublisher(Node):
    """Odometry 메시지를 받아서 TF로 브로드캐스트"""
    
    def __init__(self):
        super().__init__('odom_tf_publisher')
        
        # Parameters
        self.declare_parameter('odom_topic', '/odom')
        self.declare_parameter('odom_frame', 'odom')
        self.declare_parameter('base_frame', 'base_footprint')
        
        odom_topic = self.get_parameter('odom_topic').value
        self.odom_frame = self.get_parameter('odom_frame').value
        self.base_frame = self.get_parameter('base_frame').value
        
        # TF Broadcaster
        self.tf_broadcaster = TransformBroadcaster(self)
        
        # Subscriber
        self.odom_sub = self.create_subscription(
            Odometry,
            odom_topic,
            self.odom_callback,
            10
        )
        
        self.get_logger().info('='*60)
        self.get_logger().info('🚀 Odom TF Publisher 시작!')
        self.get_logger().info(f'  Odom 토픽: {odom_topic}')
        self.get_logger().info(f'  TF: {self.odom_frame} → {self.base_frame}')
        self.get_logger().info('='*60)
    
    def odom_callback(self, msg):
        """Odometry 메시지를 TF로 변환"""
        
        # TransformStamped 메시지 생성
        t = TransformStamped()
        
        # Header
        t.header.stamp = msg.header.stamp
        t.header.frame_id = self.odom_frame
        t.child_frame_id = self.base_frame
        
        # Position
        t.transform.translation.x = msg.pose.pose.position.x
        t.transform.translation.y = msg.pose.pose.position.y
        t.transform.translation.z = msg.pose.pose.position.z
        
        # Orientation
        t.transform.rotation = msg.pose.pose.orientation
        
        # TF 발행
        self.tf_broadcaster.sendTransform(t)


def main(args=None):
    rclpy.init(args=args)
    
    node = OdomTFPublisher()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        node.get_logger().info('\n종료 중...')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

