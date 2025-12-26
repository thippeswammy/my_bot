import os
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from ament_index_python.packages import get_package_share_directory
from launch_ros.actions import Node

def generate_launch_description():
    pkg_my_bot = get_package_share_directory('my_bot')
    pkg_my_bot_3d_nav = get_package_share_directory('my_bot_3d_nav')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')
    
    # Arguments
    map_file_arg = DeclareLaunchArgument(
        'map_file',
        default_value='map.pcd',
        description='Full path to .pcd file to load'
    )
    
    world_arg = DeclareLaunchArgument(
        'world',
        default_value=os.path.join(pkg_my_bot, 'worlds', 'ramps.world'),
        description='World file'
    )

    # 1. Launch Simulation
    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_my_bot, 'launch', 'launch_sim.launch.py')
        ),
        launch_arguments={'world': LaunchConfiguration('world'), 'gui': 'true'}.items()
    )

    # 2. Publish PCD Map (The 3D Map)
    # Publishes to /map_cloud
    pcd_publisher = Node(
        package='pcl_ros',
        executable='pcd_to_pointcloud',
        name='pcd_to_pointcloud',
        output='screen',
        parameters=[{
            'file_name': LaunchConfiguration('map_file'),
            'interval': 1.0, # Publish every second
            'frame_id': 'map',
            'latch': True
        }],
        remappings=[('cloud_pcd', '/map_cloud')]
    )

    # 3. Octomap Server (Converts PCD -> Occupancy Grid for Nav2)
    # Listen to /map_cloud, Output /projected_map
    octomap_server = Node(
        package='octomap_server',
        executable='octomap_server_node',
        name='octomap_server',
        output='screen',
        parameters=[{
            'resolution': 0.05,
            'frame_id': 'map',
            'base_frame_id': 'base_link',
            'sensor_model/max_range': 100.0, # Trust the static map
            'latch': True
        }],
        remappings=[
            ('cloud_in', '/map_cloud')
        ]
    )

    # 4. SLAM (For Localization / Map->Odom TF)
    # We use lidarslam in standard mode. It handles map->odom. 
    # It will build a new map on top, but generally align with the start.
    lidarslam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_my_bot_3d_nav, 'launch', 'lidarslam_mapping.launch.py')
        ),
        launch_arguments={'use_sim_time': 'true'}.items()
    )

    # 5. Nav2 (Planning)
    # We use our modified config that listens to /projected_map
    nav2_params_file = os.path.join(pkg_my_bot_3d_nav, 'config', 'nav2_params_3d.yaml')
    
    nav2_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, 'launch', 'navigation_launch.py')
        ),
        launch_arguments={
            'use_sim_time': 'true',
            'params_file': nav2_params_file
        }.items()
    )

    # 6. RViz
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
        world_arg,
        sim_launch,
        pcd_publisher,
        octomap_server,
        TimerAction(period=5.0, actions=[lidarslam_launch]), # Wait for sim
        TimerAction(period=10.0, actions=[nav2_launch]),
        TimerAction(period=12.0, actions=[rviz])
    ])
