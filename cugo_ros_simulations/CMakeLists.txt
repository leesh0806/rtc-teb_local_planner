cmake_minimum_required(VERSION 3.5)
project(cugo_ros2_control)

if(NOT CMAKE_C_STANDARD)
  set(CMAKE_C_STANDARD 99)
endif()

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

add_compile_options(-Wall -Wextra -Wpedantic)

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)

add_executable(cugo_ros2_control src/cugo_ros2_control.cpp)
ament_target_dependencies(cugo_ros2_control
  rclcpp
  std_msgs
  geometry_msgs
  nav_msgs
  tf2
  tf2_ros
  tf2_geometry_msgs
)

target_include_directories(cugo_ros2_control PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>
)

install(TARGETS cugo_ros2_control
  DESTINATION lib/${PROJECT_NAME})

install(DIRECTORY include/
  DESTINATION include/
)

install(DIRECTORY launch config models rviz worlds
  DESTINATION share/${PROJECT_NAME}/
)

# Python 스크립트 설치 추가
install(PROGRAMS
  scripts/gazebo_with_bridge.py
  scripts/spawn_robot.py
  scripts/robot_state_publisher_node.py
  scripts/laser_scan_filter_node.py
  scripts/odom_tf_publisher.py
  DESTINATION lib/${PROJECT_NAME}
)


ament_package()