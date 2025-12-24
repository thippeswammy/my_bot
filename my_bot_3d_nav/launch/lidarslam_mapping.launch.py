import os
from launch import LaunchDescription
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    pkg_my_bot_3d_nav = get_package_share_directory('my_bot_3d_nav')
    
    # Configuration file
    main_param_dir_arg = DeclareLaunchArgument(
        'main_param_dir',
        default_value=os.path.join(pkg_my_bot_3d_nav, 'config', 'my_lidarslam.yaml'),
        description='Full path to main parameter file to load'
    )

    use_sim_time_arg = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true'
    )

    # Scan Matcher
    scan_matcher = Node(
        package='scanmatcher',
        executable='scanmatcher_node',
        parameters=[
            LaunchConfiguration('main_param_dir'),
            {'use_sim_time': LaunchConfiguration('use_sim_time')}
        ],
        remappings=[('/input_cloud', '/velodyne_points'), ('/map', '/map_cloud')],
        output='screen'
    )

    # Graph Based Slam
    graph_based_slam = Node(
        package='graph_based_slam',
        executable='graph_based_slam_node',
        parameters=[
            LaunchConfiguration('main_param_dir'),
            {'use_sim_time': LaunchConfiguration('use_sim_time')}
        ],
        output='screen'
    )
    
    return LaunchDescription([
        main_param_dir_arg,
        use_sim_time_arg,
        scan_matcher,
        graph_based_slam,
    ])
