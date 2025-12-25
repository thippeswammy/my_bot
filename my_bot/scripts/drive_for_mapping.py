#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist
import time
import random

class Mapper(Node):
    def __init__(self):
        super().__init__('auto_mapper')
        self.publisher_ = self.create_publisher(Twist, '/cmd_vel', 10)
        self.timer = self.create_timer(0.2, self.timer_callback)
        self.start_time = self.get_clock().now()
        # State: 0=Forward, 1=Turn, 2=Reverse, 3=Stop (Scan)
        self.state = 3 # Start with a Stop/Scan
        self.state_start_time = self.get_clock().now()
        self.current_duration = 2.0 # Initial Stop

    def timer_callback(self):
        msg = Twist()
        current_time = self.get_clock().now()
        elapsed_in_state = (current_time - self.state_start_time).nanoseconds / 1e9

        if elapsed_in_state > self.current_duration:
            # Transition Logic
            self.state_start_time = current_time
            state_roll = random.random()
            
            if self.state == 3: # Was Stopped, now Move
                # 70% Forward, 30% Turn
                if state_roll < 0.7:
                    self.state = 0 # Forward
                    self.current_duration = random.uniform(2.0, 4.0)
                    self.get_logger().info(f'Switching to FORWARD for {self.current_duration:.2f}s')
                else:
                    self.state = 1 # Turn
                    self.current_duration = random.uniform(1.5, 3.0)
                    self.get_logger().info(f'Switching to TURN for {self.current_duration:.2f}s')
            
            elif self.state == 0: # Was Forward -> Stop
                self.state = 3 # Stop
                self.current_duration = 2.0
                self.get_logger().info(f'Switching to STOP (Scan) for {self.current_duration:.2f}s')

            elif self.state == 1: # Was Turn -> Stop or Forward?
                # Turn -> Stop
                self.state = 3 # Stop
                self.current_duration = 2.0
                self.get_logger().info(f'Switching to STOP (Scan) for {self.current_duration:.2f}s')

            elif self.state == 2: # Was Reverse -> Turn (Safety)
                self.state = 1 # Turn
                self.current_duration = 2.0
                self.get_logger().info(f'Switching to TURN for {self.current_duration:.2f}s')

        # Actuation
        if self.state == 0: # Forward
            msg.linear.x = 0.5
            msg.angular.z = 0.0
        elif self.state == 1: # Turn
            msg.linear.x = 0.0 
            msg.angular.z = 0.8 # Spin
        elif self.state == 2: # Reverse
            msg.linear.x = -0.3
            msg.angular.z = -0.2
        elif self.state == 3: # Stop
            msg.linear.x = 0.0
            msg.angular.z = 0.0

        self.publisher_.publish(msg)

def main():
    rclpy.init()
    mapper = Mapper()
    try:
        rclpy.spin(mapper)
    except KeyboardInterrupt:
        pass
    except SystemExit:
        pass
    finally:
        # Stop the robot
        stop_msg = Twist()
        mapper.publisher_.publish(stop_msg)
        mapper.destroy_node()
        rclpy.shutdown()

if __name__ == '__main__':
    main()
