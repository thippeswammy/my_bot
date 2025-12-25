#!/bin/bash
# Records data for offline 3D SLAM mapping
# Usage: ros2 run my_bot_3d_nav record_data.sh [optional_bag_name]

BAG_NAME=${1:-"mapping_data_$(date +%Y%m%d_%H%M%S)"}

echo "Recording data to bag: ${BAG_NAME}..."
echo "Topics: /velodyne_points /odom /tf /tf_static /robot_description"

# Record essential topics
ros2 bag record -o ${BAG_NAME} \
  /velodyne_points \
  /odom \
  /imu \
  /tf \
  /tf_static \
  /robot_description \
  /joint_states
