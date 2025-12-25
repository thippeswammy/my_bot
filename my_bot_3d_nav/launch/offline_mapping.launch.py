import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_my_bot_3d_nav = get_package_share_directory('my_bot_3d_nav')
    
    bag_file_arg = DeclareLaunchArgument(
        'bag_file',
        description='Full path to the rosbag directory (or db3 file)'
    )

    # 1. Play Rosbag
    # --clock publishes /clock for simulation time
    # -r 0.5 slows down playback to allow SLAM to process without TF lag
    play_bag = ExecuteProcess(
        cmd=['ros2', 'bag', 'play', LaunchConfiguration('bag_file'), '--clock', '-r', '0.5'],
        output='screen'
    )

    # 2. Launch 3D SLAM (LidarSLAM)
    # We use nav_3d.launch.py but we only care about the SLAM part.
    # Actually, nav_3d.launch.py launches simulation (Gazebo) by default! 
    # We must NOT launch Gazebo if we are playing a bag.
    # So we should use `lidarslam_mapping.launch.py` directly.

    lidarslam_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_my_bot_3d_nav, 'launch', 'lidarslam_mapping.launch.py')
        ),
        launch_arguments={
            'use_sim_time': 'true'
        }.items()
    )

    # 3. RViz
    rviz_config = os.path.join(pkg_my_bot_3d_nav, 'rviz', 'offline.rviz')
    rviz = ExecuteProcess(
        cmd=['ros2', 'run', 'rviz2', 'rviz2', '-d', rviz_config],
        output='screen'
    )

    return LaunchDescription([
        bag_file_arg,
        play_bag,
        lidarslam_launch,
        rviz
    ])
