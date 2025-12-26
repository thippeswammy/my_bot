#include <cmath>
#include <grid_map_core/iterators/GridMapIterator.hpp>
#include <grid_map_core/iterators/SubmapIterator.hpp>
#include <grid_map_msgs/msg/grid_map.hpp>
#include <grid_map_ros/grid_map_ros.hpp>
#include <nav_msgs/msg/occupancy_grid.hpp>
#include <pcl/io/pcd_io.h>
#include <pcl/point_types.h>
#include <pcl_conversions/pcl_conversions.h>
#include <rclcpp/rclcpp.hpp>

using namespace grid_map;

class TraversabilityLoader : public rclcpp::Node {
public:
  TraversabilityLoader() : Node("traversability_loader") {
    // Parameters
    this->declare_parameter("pcd_filename", "");
    this->declare_parameter("resolution", 0.05);
    this->declare_parameter("map_frame_id", "map");
    this->declare_parameter("slope_threshold", 0.15); // ~8.5 degrees
    this->declare_parameter("roughness_threshold", 0.05);

    std::string pcd_filename = this->get_parameter("pcd_filename").as_string();
    double resolution = this->get_parameter("resolution").as_double();
    std::string map_frame_id = this->get_parameter("map_frame_id").as_string();

    // Publishers
    auto qos = rclcpp::QoS(rclcpp::KeepLast(1)).transient_local().reliable();
    grid_map_pub_ = this->create_publisher<grid_map_msgs::msg::GridMap>(
        "traversability_grid", qos);
    occupancy_grid_pub_ = this->create_publisher<nav_msgs::msg::OccupancyGrid>(
        "traversability_map", qos);

    if (pcd_filename.empty()) {
      RCLCPP_ERROR(this->get_logger(), "No PCD filename provided.");
      return;
    }

    processPCD(pcd_filename, resolution, map_frame_id);
  }

private:
  rclcpp::Publisher<grid_map_msgs::msg::GridMap>::SharedPtr grid_map_pub_;
  rclcpp::Publisher<nav_msgs::msg::OccupancyGrid>::SharedPtr
      occupancy_grid_pub_;

  void processPCD(const std::string &filename, double resolution,
                  const std::string &frame_id) {
    pcl::PointCloud<pcl::PointXYZ>::Ptr cloud(
        new pcl::PointCloud<pcl::PointXYZ>);
    if (pcl::io::loadPCDFile<pcl::PointXYZ>(filename, *cloud) == -1) {
      RCLCPP_ERROR(this->get_logger(), "Couldn't read file: %s",
                   filename.c_str());
      return;
    }

    RCLCPP_INFO(this->get_logger(), "Loaded PCD with %lu points.",
                cloud->points.size());

    // 1. Initialize Grid Map
    GridMap map({"elevation", "slope", "roughness", "traversability"});
    map.setFrameId(frame_id);
    // Determine bounds
    double min_x = std::numeric_limits<double>::max();
    double max_x = std::numeric_limits<double>::lowest();
    double min_y = std::numeric_limits<double>::max();
    double max_y = std::numeric_limits<double>::lowest();

    for (const auto &point : cloud->points) {
      if (point.x < min_x)
        min_x = point.x;
      if (point.x > max_x)
        max_x = point.x;
      if (point.y < min_y)
        min_y = point.y;
      if (point.y > max_y)
        max_y = point.y;
    }

    // Add some padding
    double padding = 1.0;
    Length length(max_x - min_x + padding, max_y - min_y + padding);
    Position position((max_x + min_x) / 2.0, (max_y + min_y) / 2.0);
    map.setGeometry(length, resolution, position);

    RCLCPP_INFO(this->get_logger(), "Grid Map initialized. Size: %f x %f",
                length(0), length(1));

    // 2. Fill Elevation (Max Z)
    for (const auto &point : cloud->points) {
      Position pos(point.x, point.y);
      if (map.isInside(pos)) {
        float &elevation = map.atPosition("elevation", pos);
        if (std::isnan(elevation) || point.z > elevation) {
          elevation = point.z;
        }
      }
    }

    // Fill empty cells assuming ground? No, leave them NaN or handle later.
    // For traversability, NaNs usually mean unknown space.

    // 3. Compute Slope & Roughness (Simple convolution)
    // We can iterate the map
    double slope_thresh = this->get_parameter("slope_threshold").as_double();
    // double roughness_thresh =
    // this->get_parameter("roughness_threshold").as_double();

    for (GridMapIterator iterator(map); !iterator.isPastEnd(); ++iterator) {
      Position3 point;
      map.getPosition3("elevation", *iterator, point);

      if (std::isnan(point.z()))
        continue;

      // Simple slope: max diff with neighbors
      // This is a naive implementation. Grid Map has filters for this but we do
      // it manually to reduce dependency complexity for now.
      double max_diff = 0.0;

      // Check 4-connected neighbors
      Index index = *iterator;
      int dirs[4][2] = {{1, 0}, {-1, 0}, {0, 1}, {0, -1}};
      for (auto &d : dirs) {
        Index neighbor(index(0) + d[0], index(1) + d[1]);
        if (map.isValid(neighbor)) {
          double neighbor_z = map.at("elevation", neighbor);
          if (!std::isnan(neighbor_z)) {
            double diff = std::abs(point.z() - neighbor_z);
            if (diff > max_diff)
              max_diff = diff;
          }
        }
      }

      // Slope approx = max_diff / resolution (tan theta)
      double slope = max_diff / resolution;
      map.at("slope", *iterator) = slope;

      // Traversability: 0 (Good) to 100 (Bad)
      if (slope > slope_thresh) {
        map.at("traversability", *iterator) = 100.0; // Lethal
      } else {
        map.at("traversability", *iterator) = 0.0; // Free
      }
    }

    // 4. Publish
    auto grid_message = GridMapRosConverter::toMessage(map);
    grid_map_pub_->publish(*grid_message);

    nav_msgs::msg::OccupancyGrid occ_msg;
    // Mapping 0-100 float to 0-100 int8
    GridMapRosConverter::toOccupancyGrid(map, "traversability", 0.0, 100.0,
                                         occ_msg);
    occupancy_grid_pub_->publish(occ_msg);

    RCLCPP_INFO(this->get_logger(), "Published GridMap and OccupancyGrid.");
  }
};

int main(int argc, char **argv) {
  rclcpp::init(argc, argv);
  rclcpp::spin(std::make_shared<TraversabilityLoader>());
  rclcpp::shutdown();
  return 0;
}
