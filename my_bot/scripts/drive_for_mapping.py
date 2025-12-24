#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time

class Mapper(Node):
    def __init__(self):
        super().__init__('auto_mapper')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(0.1, self.timer_callback)
        self.start_time = time.time()
        self.state = 0 # 0: Forward, 1: Turn, 2: Forward, 3: Stop

    def timer_callback(self):
        msg = Twist()
        elapsed = time.time() - self.start_time

        # Simple pattern: Forward -> Turn -> Forward -> Turn to scan area
        if elapsed < 10.0:
            msg.linear.x = 0.5
            msg.angular.z = 0.0
        elif elapsed < 15.0:
            msg.linear.x = 0.0
            msg.angular.z = 0.5
        elif elapsed < 25.0:
             msg.linear.x = 0.5
             msg.angular.z = 0.0
        elif elapsed < 40.0:
             msg.linear.x = 0.0
             msg.angular.z = 0.8 # Spin to see everything
        else:
            msg.linear.x = 0.0
            msg.angular.z = 0.0
            self.publisher_.publish(msg)
            self.get_logger().info('Mapping drive complete.')
            raise SystemExit

        self.publisher_.publish(msg)

def main():
    rclpy.init()
    mapper = Mapper()
    try:
        rclpy.spin(mapper)
    except SystemExit:
        pass
    mapper.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
