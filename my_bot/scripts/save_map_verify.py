#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from sensor_msgs.msg import PointCloud2
import struct

class MapSaver(Node):
    def __init__(self):
        super().__init__('map_saver_verifier')
        self.subscription = self.create_subscription(
            PointCloud2,
            '/map_cloud',
            self.listener_callback,
            10)
        self.get_logger().info('Waiting for /map_cloud topic...')

    def listener_callback(self, msg):
        self.get_logger().info(f'Received map with {msg.width * msg.height} points. Saving to map_final.pcd...')
        # Simple PCD writer (ASCII for verification)
        with open('map_final.pcd', 'w') as f:
            f.write("# .PCD v0.7 - Point Cloud Data file format\n")
            f.write("VERSION 0.7\n")
            f.write("FIELDS x y z intensity\n")
            f.write("SIZE 4 4 4 4\n")
            f.write("TYPE F F F F\n")
            f.write("COUNT 1 1 1 1\n")
            f.write(f"WIDTH {msg.width * msg.height}\n")
            f.write("HEIGHT 1\n")
            f.write("VIEWPOINT 0 0 0 1 0 0 0\n")
            f.write(f"POINTS {msg.width * msg.height}\n")
            f.write("DATA ascii\n")
            
            # Extract points (assuming x,y,z,intensity float32 layout)
            # This is a basic parser for verification
            import sensor_msgs_py.point_cloud2 as pc2
            for point in pc2.read_points(msg, field_names=("x", "y", "z", "intensity"), skip_nans=True):
                f.write(f"{point[0]} {point[1]} {point[2]} {point[3]}\n")
        
        self.get_logger().info('Map saved successfully. Shutting down.')
        rclpy.shutdown()

def main(args=None):
    rclpy.init(args=args)
    map_saver = MapSaver()
    try:
        rclpy.spin(map_saver)
    except SystemExit:
        pass
    except Exception as e:
        print(f"Error: {e}")
    finally:
        if rclpy.ok():
            rclpy.shutdown()

if __name__ == '__main__':
    main()
