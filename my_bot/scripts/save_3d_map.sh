#!/bin/bash

# Default map name
MAP_NAME="my_3d_map.bt"

if [ -n "$1" ]; then
    MAP_NAME="$1"
fi

echo "Saving OctoMap to ${MAP_NAME}..."
ros2 run octomap_server octomap_saver_node --ros-args -p octomap_path:=${MAP_NAME}

if [ $? -eq 0 ]; then
    echo "Map saved successfully!"
else
    echo "Failed to save map. Is octomap_server running?"
fi
