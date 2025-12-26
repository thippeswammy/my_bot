cmake_minimum_required(VERSION 3.8)
project(my_bot_3d_nav)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(my_bot REQUIRED)
find_package(nav2_bringup REQUIRED)
find_package(nav2_common REQUIRED)
find_package(rviz2 REQUIRED)
find_package(grid_map_ros REQUIRED)
find_package(grid_map_msgs REQUIRED)
find_package(grid_map_pcl REQUIRED)
find_package(pcl_conversions REQUIRED)
find_package(PCL REQUIRED COMPONENTS common io filters)

install(DIRECTORY
  launch
  config
  rviz
  DESTINATION share/${PROJECT_NAME}
)

add_executable(traversability_loader src/traversability_loader.cpp)
ament_target_dependencies(traversability_loader
  rclcpp
  grid_map_ros
  grid_map_msgs
  grid_map_pcl
  pcl_conversions
)
# PCL is a system dependency, link it slightly differently usually, but let's try standard include
include_directories(${PCL_INCLUDE_DIRS})
link_directories(${PCL_LIBRARY_DIRS})
add_definitions(${PCL_DEFINITIONS})
target_link_libraries(traversability_loader ${PCL_LIBRARIES})

install(TARGETS traversability_loader
  DESTINATION lib/${PROJECT_NAME}
)

install(PROGRAMS
  scripts/save_3d_map.sh
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips the linter which checks for license file
  # comment the line when a license file is added to the project
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
