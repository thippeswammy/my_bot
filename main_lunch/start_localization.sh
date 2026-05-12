#!/bin/bash
# =======================================================
# 📍 ROS 2 Localization & Navigation Launcher
# Launches Simulation, Map Server, AMCL, and Nav2
# Uses your saved map: my_map_save2.yaml
# =======================================================

# --- CONFIG ---
WORKSPACE=/home/thippe/workspaces/Robot/my_bot_ws
ROS_DISTRO=humble
DELAY=5

# --- SOURCE ENVIRONMENT ---
source /opt/ros/$ROS_DISTRO/setup.bash
source $WORKSPACE/install/setup.bash
echo "✅ Environment sourced from: $WORKSPACE"

# --- COMMANDS ---
# 1. Gazebo Simulation
CMD1="source /opt/ros/$ROS_DISTRO/setup.bash; source $WORKSPACE/install/setup.bash; echo '🧱 Launching Gazebo Simulation...'; ros2 launch my_bot launch_sim.launch.py world:=$WORKSPACE/src/my_bot/worlds/obstacles.world; exec bash"

# 2. Nav2 Bringup (Map Server + AMCL + Navigation)
MAP_FILE=$WORKSPACE/src/my_bot/my_map/map2/my_map_save2.yaml
CMD2="source /opt/ros/$ROS_DISTRO/setup.bash; source $WORKSPACE/install/setup.bash; echo '📍 Launching Localization & Navigation...'; ros2 launch nav2_bringup bringup_launch.py use_sim_time:=true map:=$MAP_FILE; exec bash"

# 3. RViz2
CMD3="source /opt/ros/$ROS_DISTRO/setup.bash; source $WORKSPACE/install/setup.bash; echo '🪞 Launching RViz2...'; rviz2 -d $WORKSPACE/src/my_bot/config/view_robot.rviz; exec bash"

# --- OPEN FIRST TAB ---
gnome-terminal --tab --title="Gazebo Simulation" -- bash -c "$CMD1"

# --- WAIT AND OPEN OTHER TABS ---
sleep $DELAY
gnome-terminal --tab --title="Localization & Nav" -- bash -c "$CMD2"

sleep 2
gnome-terminal --tab --title="RViz2" -- bash -c "$CMD3"

echo "🚀 Robot launched in Localization Mode!"
echo "👉 In RViz, use '2D Pose Estimate' to set the robot's initial position on the map."
