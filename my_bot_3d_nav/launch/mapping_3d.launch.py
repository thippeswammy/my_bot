from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument

def generate_launch_description():
    frame_id_arg = DeclareLaunchArgument(
        'frame_id',
        default_value='map',
        description='Frame ID for Octomap'
    )

    return LaunchDescription([
        frame_id_arg,
        Node(
            package='octomap_server',
            executable='octomap_server_node',
            name='octomap_server',
            output='screen',
            parameters=[{
                'resolution': 0.05,
                'frame_id': LaunchConfiguration('frame_id'),
                'sensor_model/max_range': 10.0,
                'sensor_model/hit': 0.7,
                'sensor_model/miss': 0.4,
                'sensor_model/min': 0.12,
                'sensor_model/max': 0.97,
                'data_type': 'PointCloud2',
                'base_frame_id': 'base_link'
            }],
            remappings=[
                ('cloud_in', '/velodyne_points')
            ]
        )
    ])
