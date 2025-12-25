#!/bin/bash
# Triggers the map save in lidarslam_ros2
# Saves to 'map.pcd' in the directory where the SLAM node was launched (or PWD).

echo "Requesting Map Save..."
ros2 service call /map_save std_srvs/srv/Empty "{}"
echo "Check your current directory (or ~/.ros) for 'map.pcd'"
