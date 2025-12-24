from launch import LaunchDescription
from launch_ros.actions import Node
from launch.substitutions import LaunchConfiguration
from launch.actions import DeclareLaunchArgument
from launch.substitutions import PythonExpression

def generate_launch_description():
    map_path_arg = DeclareLaunchArgument(
        'map_path',
        default_value='',
        description='Path to .bt map file to load'
    )

    enable_mapping_arg = DeclareLaunchArgument(
        'enable_mapping',
        default_value='true',
        description='Whether to subscribe to pointcloud and update map'
    )
    
    # If enable_mapping is 'true', subscribe to /velodyne_points.
    # If 'false', subscribe to /dummy_cloud required to just read static map.
    cloud_remap_topic = PythonExpression([
        "'/velodyne_points' if '", LaunchConfiguration('enable_mapping'), "' == 'true' else '/octomap/idle'"
    ])

    return LaunchDescription([
        frame_id_arg,
        map_path_arg,
        enable_mapping_arg,
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
                'base_frame_id': 'base_link',
                'octomap_path': LaunchConfiguration('map_path')
            }],
            remappings=[
                ('cloud_in', cloud_remap_topic)
            ]
        )
    ])
