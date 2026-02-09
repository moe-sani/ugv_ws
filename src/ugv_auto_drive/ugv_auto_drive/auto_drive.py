#!/usr/bin/env python3
"""Auto drive node: drive forward 5cm, stop 5s, repeat 3 times, then exit."""
import time

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


def main():
    rclpy.init()
    node = Node('ugv_auto_drive')
    pub = node.create_publisher(Twist, 'cmd_vel', 10)

    # Settings
    distance_m = 0.05  # 5 cm
    speed_m_s = 0.10   # 10 cm/s
    stop_seconds = 5.0
    rounds = 3

    if speed_m_s <= 0:
        node.get_logger().error('speed_m_s must be > 0')
        return

    move_duration = distance_m / speed_m_s

    move_twist = Twist()
    move_twist.linear.x = float(speed_m_s)

    stop_twist = Twist()

    for i in range(rounds):
        node.get_logger().info(f'Round {i+1}/{rounds}: driving {distance_m*100:.1f}cm')
        pub.publish(move_twist)
        rclpy.spin_once(node, timeout_sec=0.01)
        time.sleep(move_duration)

        pub.publish(stop_twist)
        rclpy.spin_once(node, timeout_sec=0.01)
        node.get_logger().info(f'Stopped for {stop_seconds}s')
        time.sleep(stop_seconds)

    # Ensure stopped
    pub.publish(stop_twist)
    rclpy.spin_once(node, timeout_sec=0.01)
    node.get_logger().info('Auto drive routine completed. Exiting.')
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
