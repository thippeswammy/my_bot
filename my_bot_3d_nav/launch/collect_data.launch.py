import os
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, ExecuteProcess, IncludeLaunchDescription, TimerAction
from launch.substitutions import LaunchConfiguration
from launch.launch_description_sources import PythonLaunchDescriptionSource
from ament_index_python.packages import get_package_share_directory

def generate_launch_description():
    pkg_my_bot = get_package_share_directory('my_bot')
    pkg_my_bot_3d_nav = get_package_share_directory('my_bot_3d_nav')

    # Default world
    world_arg = DeclareLaunchArgument(
        'world',
        default_value=os.path.join(pkg_my_bot, 'worlds', 'ramps.world'),
        description='Full path to world model file to load'
    )

    # 1. Launch Simulation (Gazebo + Robot + Controllers)
    # This brings up the robot, publishes /robot_description, and starts controllers
    sim_launch = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(pkg_my_bot, 'launch', 'launch_sim.launch.py')
        ),
        launch_arguments={'world': LaunchConfiguration('world')}.items()
    )

    # 2. Record Rosbag
    # We record all topics necessary for offline SLAM
    # - /velodyne_points: Pointcloud data
    # - /diff_cont/odom: Odometry from differential drive controller
    # - /tf, /tf_static: Transforms (odom->base_link, etc.)
    # - /robot_description: Robot URDF
    # - /joint_states: Joint positions
    # - /clock: Simulation time
    record_bag = ExecuteProcess(
        cmd=[
            'ros2', 'bag', 'record',
            '-o', 'my_mapping_bag',
            '/velodyne_points',
            '/diff_cont/odom',
            '/tf',
            '/tf_static',
            '/robot_description',
            '/joint_states',
            '/clock'
        ],
        output='screen'
    )

    # 3. RViz for monitoring
    # Using the offline configuration to visualize the robot and data
    rviz_config = os.path.join(pkg_my_bot_3d_nav, 'rviz', 'offline.rviz')
    rviz = ExecuteProcess(
        cmd=['ros2', 'run', 'rviz2', 'rviz2', '-d', rviz_config],
        output='screen'
    )

    # Delayed Bag Recording
    delayed_record_bag = TimerAction(
        period=60.0,
        actions=[record_bag]
    )

    return LaunchDescription([
        world_arg,
        sim_launch,
        # delayed_record_bag, # Manual recording
        rviz
    ])
