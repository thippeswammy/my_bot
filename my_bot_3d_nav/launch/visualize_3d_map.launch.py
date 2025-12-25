import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_my_bot_3d_nav = get_package_share_directory('my_bot_3d_nav')
    
    # Default map path (assuming user saved it to home or workspace)
    # User can override: ros2 launch ... map_file:=/path/to/my.pcd
    map_file_arg = DeclareLaunchArgument(
        'map_file',
        default_value='map.pcd',
        description='Full path to .pcd file to load'
    )

    # PCD Publisher
    # Uses pcl_ros to publish a static PointCloud2
    pcd_publisher = Node(
        package='pcl_ros',
        executable='pcd_to_pointcloud',
        name='pcd_to_pointcloud',
        output='screen',
        parameters=[{
            'file_name': LaunchConfiguration('map_file'),
            'interval': 1.0,
            'frame_id': 'map'
        }],
        remappings=[('cloud_pcd', '/map_cloud')]
    )

    # RViz
    rviz_config = os.path.join(pkg_my_bot_3d_nav, 'rviz', 'nav_3d.rviz')
    rviz = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config],
        output='screen'
    )

    return LaunchDescription([
        map_file_arg,
        pcd_publisher,
        rviz
    ])
