import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration

def generate_launch_description():
    pkg_my_bot = get_package_share_directory('my_bot')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')
    pkg_my_bot_3d_nav = get_package_share_directory('my_bot_3d_nav')

    pkg_slam_toolbox = get_package_share_directory('slam_toolbox')

    world_path = os.path.join(pkg_my_bot, 'worlds', 'obstacles.world')
    nav_params_path = os.path.join(pkg_my_bot_3d_nav, 'config', 'nav2_params_3d.yaml')
    nav_params_odom_path = os.path.join(pkg_my_bot_3d_nav, 'config', 'nav2_params_3d_odom.yaml')
    slam_params_path = os.path.join(pkg_my_bot, 'config', 'mapper_params_online_async.yaml')
    mapping_launch_path = os.path.join(pkg_my_bot_3d_nav, 'launch', 'mapping_3d.launch.py')

    # Launch configuration variables specific to simulation
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    enable_3d_mapping = LaunchConfiguration('enable_3d_mapping', default='false')
    # Replaced use_slam with slam_type for more granularity
    slam_type = LaunchConfiguration('slam_type', default='2d') # Options: 'none', '2d', '3d'
    world = LaunchConfiguration('world', default=world_path)

    # Declare the launch arguments
    declare_use_sim_time_cmd = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true')
        
    declare_enable_3d_mapping_cmd = DeclareLaunchArgument(
        'enable_3d_mapping',
        default_value='false',
        description='Enable Octomap 3D mapping')

    declare_slam_type_cmd = DeclareLaunchArgument(
        'slam_type',
        default_value='2d',
        description='SLAM type to use: "none" (Odom), "2d" (Slam Toolbox), "3d" (LidarSLAM)')

    declare_world_cmd = DeclareLaunchArgument(
        'world',
        default_value=world_path,
        description='Full path to world model file to load')

    # Include the robot simulation
    launch_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_my_bot, 'launch', 'launch_sim.launch.py')
        ),
        launch_arguments={'world': world}.items()
    )

    # Select params file based on slam_type
    # If 2d or 3d SLAM is used, we generally use the SLAM-compatible nav params (map frame)
    # If slam_type is 'none', we use odom params.
    from launch.substitutions import PythonExpression
    params_file = PythonExpression([
        "'", nav_params_path, "' if '", slam_type, "' in ['2d', '3d'] else '", nav_params_odom_path, "'"
    ])

    # Include the navigation stack
    bringup_nav = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, 'launch', 'navigation_launch.py')
        ),
        launch_arguments={
             'use_sim_time': use_sim_time,
             'params_file': params_file
        }.items()
    )

    # 2D SLAM Toolbox (Conditionally)
    # Launch only if slam_type == '2d'
    from launch.conditions import IfCondition
    slam_toolbox = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_slam_toolbox, 'launch', 'online_async_launch.py')
        ),
        condition=IfCondition(PythonExpression(["'", slam_type, "' == '2d'"])),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'slam_params_file': slam_params_path
        }.items()
    )

    # 3D SLAM (LidarSLAM) (Conditionally)
    # Launch only if slam_type == '3d'
    lidarslam_launch_path = os.path.join(pkg_my_bot_3d_nav, 'launch', 'lidarslam_mapping.launch.py')
    lidarslam = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(lidarslam_launch_path),
        condition=IfCondition(PythonExpression(["'", slam_type, "' == '3d'"])),
        launch_arguments={
            'use_sim_time': use_sim_time,
        }.items()
    )

    # Rviz
    rviz_config_file = os.path.join(pkg_my_bot_3d_nav, 'rviz', 'nav_3d.rviz')
    
    start_rviz_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, 'launch', 'rviz_launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'rviz_config': rviz_config_file
        }.items()
    )
    
    # Octomap Mapping
    # Logic: 
    # - If slam_type == '3d', we might NOT want Octomap if LidarSLAM provides a map, 
    #   BUT Octomap is often used for the Costmap interaction specifically if LidarSLAM outputs a PointCloud2 map.
    #   LidarSLAM outputs /map (Occupancy/Grid?) and /map_cloud.
    #   For now, we keep Octomap as the "Mapping via Octomap" feature, controlled by enable_3d_mapping.
    
    mapping_frame = 'map' # Default to map if SLAM is on.
    # If slam_type == 'none', use odom.
    mapping_frame_exp = PythonExpression([
        "'map' if '", slam_type, "' in ['2d', '3d'] else 'odom'"
    ])

    
    declare_map_file_cmd = DeclareLaunchArgument(
        'map_file',
        default_value='',
        description='Full path to .bt OctoMap file to load (optional)')

    # Logic for Octomap launch matches previous:
    should_launch_octomap = PythonExpression([
        "'", enable_3d_mapping, "' == 'true' or '", LaunchConfiguration('map_file'), "' != ''"
    ])

    start_mapping_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(mapping_launch_path),
        condition=IfCondition(should_launch_octomap),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'frame_id': mapping_frame_exp,
            'map_path': LaunchConfiguration('map_file'),
            'enable_mapping': enable_3d_mapping
        }.items()
    )

    from launch.actions import TimerAction

    delayed_nav_launch = TimerAction(
        period=15.0,
        actions=[
            bringup_nav,
            slam_toolbox,
            lidarslam,
            start_mapping_cmd,
            start_rviz_cmd
        ]
    )

    return LaunchDescription([
        declare_use_sim_time_cmd,
        declare_enable_3d_mapping_cmd,
        declare_slam_type_cmd,
        declare_world_cmd,
        declare_map_file_cmd,
        launch_sim,
        delayed_nav_launch
    ])
