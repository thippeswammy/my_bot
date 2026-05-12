#!/bin/bash
# =======================================================
# 🧭 ROS 2 Navigation Stack Launcher (All in One Terminal)
# Launches Simulation, SLAM, Nav2, TwistMux, and RViz2
# Each in its own tab with 2s delay
# =======================================================

# --- CONFIG ---
WORKSPACE=/home/thippe/workspaces/Robot/my_bot_ws         # Change if your workspace name is different
ROS_DISTRO=humble
DELAY=2                      # seconds between tab launches

# --- SOURCE ENVIRONMENT ---
source /opt/ros/$ROS_DISTRO/setup.bash
source $WORKSPACE/install/setup.bash
echo "✅ Environment sourced from: $WORKSPACE"

# --- COMMANDS ---
CMD1="source /opt/ros/$ROS_DISTRO/setup.bash; source $WORKSPACE/install/setup.bash; echo '🧱 Launching Gazebo Simulation...'; ros2 launch my_bot launch_sim.launch.py world:=$WORKSPACE/src/my_bot/worlds/obstacles.world; exec bash"
CMD2="source /opt/ros/$ROS_DISTRO/setup.bash; source $WORKSPACE/install/setup.bash; echo '🗺️ Launching SLAM Toolbox...'; ros2 launch slam_toolbox online_async_launch.py slam_params_file:=$WORKSPACE/src/my_bot/config/mapper_params_online_async.yaml use_sim_time:=true; exec bash"
CMD3="source /opt/ros/$ROS_DISTRO/setup.bash; source $WORKSPACE/install/setup.bash; echo '🤖 Launching Nav2 Navigation...'; ros2 launch nav2_bringup navigation_launch.py use_sim_time:=true; exec bash"
CMD4="source /opt/ros/$ROS_DISTRO/setup.bash; source $WORKSPACE/install/setup.bash; echo '🪞 Launching RViz2...'; rviz2 -d $WORKSPACE/src/my_bot/config/view_robot.rviz; exec bash"

# --- OPEN FIRST TAB ---
gnome-terminal --tab --title="Gazebo Simulation" -- bash -c "$CMD1"

# --- WAIT AND OPEN OTHER TABS ---
sleep 5 # Wait longer for Gazebo to spawn and load controllers
gnome-terminal --tab --title="SLAM Toolbox" -- bash -c "$CMD2"

sleep $DELAY
gnome-terminal --tab --title="Nav2 Navigation" -- bash -c "$CMD3"

sleep $DELAY
gnome-terminal --tab --title="RViz2" -- bash -c "$CMD4"

echo "🚀 All 4 processes launched in separate tabs!"
