#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import LaserScan, Imu

class SensorVerificationNode(Node):
    def __init__(self):
        super().__init__('sensor_verification_node')
        self.lidar_subscriber = self.create_subscription(
            LaserScan,
            '/livox/lidar',
            self.lidar_callback,
            10
        )
        self.imu_subscriber = self.create_subscription(
            Imu,
            '/livox/imu',
            self.imu_callback,
            10
        )
        self.lidar_received = False
        self.imu_received = False
        self.get_logger().info('Sensor verification node started. Waiting for sensor data...')
    
    def lidar_callback(self, msg):
        if not self.lidar_received:
            self.lidar_received = True
            self.get_logger().info('✓ Lidar data received!')
            self.get_logger().info(f'  Frame ID: {msg.header.frame_id}')
            self.get_logger().info(f'  Range min: {msg.range_min}')
            self.get_logger().info(f'  Range max: {msg.range_max}')
            self.get_logger().info(f'  Angle min: {msg.angle_min}')
            self.get_logger().info(f'  Angle max: {msg.angle_max}')
            self.get_logger().info(f'  Angle increment: {msg.angle_increment}')
            self.get_logger().info(f'  Time increment: {msg.time_increment}')
            self.get_logger().info(f'  Scan time: {msg.scan_time}')
            self.get_logger().info(f'  Number of ranges: {len(msg.ranges)}')
    
    def imu_callback(self, msg):
        if not self.imu_received:
            self.imu_received = True
            self.get_logger().info('✓ IMU data received!')
            self.get_logger().info(f'  Frame ID: {msg.header.frame_id}')
            self.get_logger().info(f'  Orientation: {msg.orientation}')
            self.get_logger().info(f'  Angular velocity: {msg.angular_velocity}')
            self.get_logger().info(f'  Linear acceleration: {msg.linear_acceleration}')
    
    def check_sensors(self):
        if self.lidar_received and self.imu_received:
            self.get_logger().info('\n✓ All sensors are working correctly!')
            return True
        return False

def main(args=None):
    rclpy.init(args=args)
    sensor_verification_node = SensorVerificationNode()
    
    try:
        rclpy.spin(sensor_verification_node)
    except KeyboardInterrupt:
        sensor_verification_node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()