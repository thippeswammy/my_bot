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
    use_slam = LaunchConfiguration('use_slam', default='true')
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

    declare_use_slam_cmd = DeclareLaunchArgument(
        'use_slam',
        default_value='true',
        description='Enable SLAM (true) or use Odom-only (false)')

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

    # Select params file based on use_slam
    from launch.substitutions import PythonExpression
    params_file = PythonExpression([
        "'", nav_params_path, "' if '", use_slam, "' == 'true' else '", nav_params_odom_path, "'"
    ])

    # Include the navigation stack
    # Note: We are using navigation_launch.py from nav2_bringup, which brings up the entire nav stack
    # but NOT the map server (by default) or localization (amcl) if we are doing SLAM or checking defaults.
    # Wait, navigation_launch.py brings up Lifecycle Manager for navigation, controller, planner, behaviors, smoother, velocity smoother.
    # It DOES NOT bring up AMCL or Map Server.
    
    bringup_nav = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, 'launch', 'navigation_launch.py')
        ),
        launch_arguments={
             'use_sim_time': use_sim_time,
             'params_file': params_file
        }.items()
    )

    # Include SLAM Toolbox (Conditionally)
    from launch.conditions import IfCondition
    slam_toolbox = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_slam_toolbox, 'launch', 'online_async_launch.py')
        ),
        condition=IfCondition(use_slam),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'slam_params_file': slam_params_path
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
    # Logic: Only launch if enable_3d_mapping is true
    # Mapping frame depends on SLAM (map) or Odom-Only (odom)
    mapping_frame = PythonExpression([
        "'map' if '", use_slam, "' == 'true' else 'odom'"
    ])
    
    declare_map_file_cmd = DeclareLaunchArgument(
        'map_file',
        default_value='',
        description='Full path to .bt OctoMap file to load (optional)')

    # ... (in LaunchDescription list) ...
    
    # Logic: 
    # 1. Launch Octomap if enable_3d_mapping is TRUE (Live Mapping)
    # 2. Launch Octomap if map_file is present (Static Map loading)
    # 3. If enable_3d_mapping is FALSE but map_file is present, load map but don't subscribe to cloud (Static Navigation)
    
    should_launch_octomap = PythonExpression([
        "'", enable_3d_mapping, "' == 'true' or '", LaunchConfiguration('map_file'), "' != ''"
    ])

    start_mapping_cmd = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(mapping_launch_path),
        condition=IfCondition(should_launch_octomap),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'frame_id': mapping_frame,
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
            start_mapping_cmd,
            start_rviz_cmd
        ]
    )

    return LaunchDescription([
        declare_use_sim_time_cmd,
        declare_enable_3d_mapping_cmd,
        declare_use_slam_cmd,
        declare_world_cmd,
        declare_map_file_cmd,
        launch_sim,
        delayed_nav_launch
    ])
