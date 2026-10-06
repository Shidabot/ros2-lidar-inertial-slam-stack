#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import sys, select, termios, tty

class TeleopNode(Node):
    def __init__(self):
        super().__init__('teleop_node')

        # ✅ 修复 topic
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)

        self.msg = Twist()
        self.speed = 3.5
        self.turn = 1.0

        self.get_logger().info('WASD控制: w/s前后, a/d转向, 空格停止, q退出')

    def get_key(self):
        tty.setraw(sys.stdin.fileno())
        rlist, _, _ = select.select([sys.stdin], [], [], 0.1)
        if rlist:
            key = sys.stdin.read(1)
        else:
            key = ''
        termios.tcsetattr(sys.stdin, termios.TCSADRAIN, settings)
        return key

def main():
    rclpy.init()
    node = TeleopNode()

    try:
        while rclpy.ok():
            key = node.get_key()

            if key == 'w':
                node.msg.linear.x = node.speed
                node.msg.angular.z = 0.0

            elif key == 's':
                node.msg.linear.x = -node.speed
                node.msg.angular.z = 0.0

            elif key == 'd':
                node.msg.linear.x = 0.0
                node.msg.angular.z = node.turn

            elif key == 'a':
                node.msg.linear.x = 0.0
                node.msg.angular.z = -node.turn

            elif key == ' ':
                node.msg.linear.x = 0.0
                node.msg.angular.z = 0.0

            elif key == 'q':
                break

            # ✅ 持续发布（关键）
            node.publisher_.publish(node.msg)

    except Exception as e:
        node.get_logger().error(str(e))

    finally:
        node.msg.linear.x = 0.0
        node.msg.angular.z = 0.0
        node.publisher_.publish(node.msg)

        node.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    settings = termios.tcgetattr(sys.stdin)
    main()