import os
from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription, DeclareLaunchArgument, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PythonExpression
from launch.conditions import IfCondition

def generate_launch_description():
    pkg_my_bot = get_package_share_directory('my_bot')
    pkg_nav2_bringup = get_package_share_directory('nav2_bringup')
    pkg_my_bot_3d_nav = get_package_share_directory('my_bot_3d_nav')

    world_path = os.path.join(pkg_my_bot, 'worlds', 'ramps.world')
    nav_params_path = os.path.join(pkg_my_bot_3d_nav, 'config', 'nav2_params_3d.yaml')
    
    # Launch arguments
    use_sim_time = LaunchConfiguration('use_sim_time', default='true')
    world = LaunchConfiguration('world', default=world_path)

    declare_use_sim_time = DeclareLaunchArgument(
        'use_sim_time',
        default_value='true',
        description='Use simulation (Gazebo) clock if true')

    declare_world = DeclareLaunchArgument(
        'world',
        default_value=world_path,
        description='Full path to world model file to load')

    # 1. Launch Simulation
    launch_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_my_bot, 'launch', 'launch_sim.launch.py')
        ),
        launch_arguments={'world': world}.items()
    )

    # 2. Launch 3D SLAM (lidarslam_ros2)
    lidarslam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_my_bot_3d_nav, 'launch', 'lidarslam_mapping.launch.py')
        ),
        launch_arguments={'use_sim_time': use_sim_time}.items()
    )

    # 3. Launch Navigation2
    # We use navigation_launch.py which brings up lifecycle manager, controller, planner, etc.
    # We assume 'map' frame is provided by lidarslam_ros2
    bringup_nav = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, 'launch', 'navigation_launch.py')
        ),
        launch_arguments={
             'use_sim_time': use_sim_time,
             'params_file': nav_params_path
        }.items()
    )

    # 4. RViz
    rviz_config_file = os.path.join(pkg_my_bot_3d_nav, 'rviz', 'nav_3d.rviz')
    start_rviz = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_nav2_bringup, 'launch', 'rviz_launch.py')
        ),
        launch_arguments={
            'use_sim_time': use_sim_time,
            'rviz_config': rviz_config_file
        }.items()
    )

    # Validating that we don't need octomap for pure navigation if we blindly trust SLAM's localization
    # But usually Nav2 needs a Costmap. Nav2 Parameters usually define inputs.
    # If users want Octomap for 3D collision avoidance, it can be added here too.
    # For now, let's keep it simple: Sim + SLAM + Nav2.

    delayed_launch = TimerAction(
        period=10.0,
        actions=[
            lidarslam_launch,
            bringup_nav,
            start_rviz
        ]
    )

    return LaunchDescription([
        declare_use_sim_time,
        declare_world,
        launch_sim,
        delayed_launch
    ])
