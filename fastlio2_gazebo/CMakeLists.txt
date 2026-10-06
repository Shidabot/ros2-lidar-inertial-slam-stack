cmake_minimum_required(VERSION 3.8)
project(fastlio2_gazebo)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(rclpy REQUIRED)
find_package(gazebo_ros REQUIRED)

# 安装启动文件
install(DIRECTORY
  launch
  models
  worlds
  DESTINATION share/${PROJECT_NAME}/
)

# 安装Python模块
ament_python_install_package(${PROJECT_NAME})

install(PROGRAMS
  fastlio2_gazebo/sensor_verification.py
  fastlio2_gazebo/teleop_node.py
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()