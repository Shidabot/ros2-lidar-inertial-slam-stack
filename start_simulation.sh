#!/bin/bash

# 启动脚本：构建和运行FASTLIO2 Gazebo仿真环境

echo "===================================="
echo "FASTLIO2 Gazebo Simulation Launcher"
echo "===================================="

# ros2 launch fastlio2_gazebo fastlio_gazebo.launch.py | tee fastlio_gazebo.log
ros2 launch fastlio2_gazebo fastlio_gazebo.launch.py 2>&1 | sed -r "s/\x1B\[([0-9]{1,3}(;[0-9]{1,3})?)?[mGK]//g" | tee fastlio_gazebo.log

echo "FASTLIO2 Gazebo Simulation Launcher Started"
