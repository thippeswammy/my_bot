
import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node

def generate_launch_description():
    pkg_share = get_package_share_directory('my_bot_3d_nav')
    
    pcd_filename_arg = DeclareLaunchArgument(
        'pcd_filename',
        default_value='/home/thippe/my_robot/my_map.pcd',
        description='Path to the PCD file to load'
    )

    traversability_node = Node(
        package='my_bot_3d_nav',
        executable='traversability_loader',
        name='traversability_loader',
        output='screen',
        parameters=[{
            'pcd_filename': LaunchConfiguration('pcd_filename'),
            'resolution': 0.05,
            'map_frame_id': 'map',
            'slope_threshold': 0.15,
            'roughness_threshold': 0.05
        }]
    )

    return LaunchDescription([
        pcd_filename_arg,
        traversability_node
    ])
