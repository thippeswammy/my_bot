#!/usr/bin/env python3
import rclpy
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from geometry_msgs.msg import PoseStamped

def main():
    rclpy.init()
    navigator = BasicNavigator()

    # Wait for Nav2
    # navigator.waitUntilNav2Active() # Might hang if AMCL missing, but we are in odom mode.
    # Actually BasicNavigator checks for Lifecycle nodes.

    # Set Goal
    goal_pose = PoseStamped()
    goal_pose.header.frame_id = 'odom'
    goal_pose.header.stamp = navigator.get_clock().now().to_msg()
    goal_pose.pose.position.x = 5.0
    goal_pose.pose.position.y = 0.0
    goal_pose.pose.orientation.w = 1.0

    print("Sending goal: x=5.0, y=0.0...")
    navigator.goToPose(goal_pose)

    i = 0
    while not navigator.isTaskComplete():
        i = i + 1
        feedback = navigator.getFeedback()
        # print('Feedback: ' + str(feedback))

    result = navigator.getResult()
    if result == TaskResult.SUCCEEDED:
        print('Goal succeeded!')
    elif result == TaskResult.CANCELED:
        print('Goal was canceled!')
    elif result == TaskResult.FAILED:
        print('Goal failed!')

    rclpy.shutdown()

if __name__ == '__main__':
    main()
