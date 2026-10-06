# SLAM-NAV

基于 ROS 2 的 LiDAR–IMU SLAM、回环优化与地图重定位工程。

> 当前仓库的实际实现是 SLAM 与定位能力，不是完整自主导航系统。仓库不包含目标点导航、全局路径规划、局部避障、代价地图或自动运动控制。

## 当前已实现的功能

### 1. `fastlio2`：实时 LiDAR–IMU 里程计与局部建图

- 订阅 LiDAR 点云和 IMU 数据。
- 使用迭代误差状态卡尔曼滤波器（IESKF）估计状态。
- 完成 IMU 初始化、状态传播和点云去畸变。
- 通过点到平面残差更新状态。
- 使用 ikd-Tree 维护局部增量点云地图。

主要输出：

```text
/fastlio2/lio_odom       nav_msgs/Odometry
/fastlio2/body_cloud     sensor_msgs/PointCloud2
/fastlio2/world_cloud    sensor_msgs/PointCloud2
/fastlio2/lio_path       nav_msgs/Path
TF: lidar → body
```

### 2. `pgo`：回环检测与位姿图优化

- 同步订阅 `fastlio2` 的机体系点云和里程计。
- 根据平移/旋转阈值选取关键帧。
- 根据空间距离和时间间隔搜索回环候选。
- 以 ICP 验证候选回环。
- 使用 GTSAM iSAM2 增量优化位姿图。
- 发布全局修正的 `map → lidar` TF 与回环可视化 Marker。

服务：

```text
/pgo/save_maps    保存优化后的地图、关键帧与位姿
```

### 3. `localizer`：基于已知地图的 ICP 重定位

- 载入外部 PCD 地图。
- 同步使用当前点云和 LiDAR 里程计。
- 执行粗配准与精配准两阶段 ICP。
- 成功时发布 `map → lidar` TF 与地图点云。

服务：

```text
/localizer/relocalize        载入地图并设置重定位初值
/localizer/relocalize_check  查询重定位是否已完成
```

### 4. `fastlio2_gazebo`：仿真与手动遥控

- 提供 Gazebo 世界、机器人 URDF 和传感器模型。
- `teleop_node.py` 可通过键盘发布 `/cmd_vel`。
- `/cmd_vel` 在当前项目中仅用于**人工遥控仿真机器人**，不是路径规划或自动控制的输出。

## 节点与数据流

```text
LiDAR + IMU
    │
    ▼
fastlio2/lio_node
    ├── /fastlio2/lio_odom
    ├── /fastlio2/body_cloud ──► pgo/pgo_node
    │                                ├── 回环检测
    │                                ├── GTSAM 优化
    │                                └── TF: map → lidar
    │
    └── /fastlio2/body_cloud ──► localizer/localizer_node
                                     ├── PCD 地图 + ICP
                                     └── TF: map → lidar
```

`pgo` 和 `localizer` 是两种不同的全局定位路径：前者用于在线建图过程的回环全局优化，后者用于在已有地图中进行 ICP 重定位。通常根据任务选择运行，不应同时发布同一条 `map → lidar` TF。

## 当前未实现的导航能力

以下内容只存在于早期设计描述中，当前仓库没有对应 ROS 2 包、节点或算法实现：

- 目标点任务接口与导航状态机。
- 全局路径规划：A*、Dijkstra、RRT* 等。
- 局部规划：DWA、TEB 或轨迹优化器。
- 2D/3D 代价地图与实时障碍物层。
- 动态障碍物检测、预测和避障。
- PID/MPC 轨迹跟踪与自动 `/cmd_vel` 发布。
- Nav2 集成。

因此，本项目目前的准确定位是：

```text
ROS 2 LiDAR–IMU SLAM + 回环优化 + ICP 重定位 + Gazebo 手动遥控
```

而不是：

```text
给定目标点 → 自动规划路径 → 动态避障 → 自动到达目标点
```

## 依赖

- ROS 2（项目使用 `rclcpp`、Python Launch 和 ROS 2 消息接口）。
- PCL、Eigen、Sophus、yaml-cpp。
- `livox_ros_driver2`。
- GTSAM（`pgo` 模块）。
- Gazebo ROS（仿真模块）。

## 启动

构建 ROS 2 工作空间后，可分别启动：

```bash
ros2 launch fastlio2 lio_launch.py
ros2 launch pgo pgo_launch.py
ros2 launch localizer localizer_launch.py
ros2 launch fastlio2_gazebo fastlio_gazebo.launch.py
```

`pgo_launch.py` 与 `localizer_launch.py` 均会同时启动 `fastlio2/lio_node`。请不要同时启动它们，除非你已自行处理重复节点、话题和 TF 发布冲突。

## 配置

- `fastlio2/config/lio.yaml`：LiDAR/IMU 话题、外参、噪声、滤波分辨率和 IESKF 参数。
- `pgo/config/pgo.yaml`：关键帧门限、回环搜索半径、ICP 分数门限和子地图参数。
- `localizer/config/localizer.yaml`：粗/精 ICP 的分辨率、最大迭代次数和匹配分数门限。

## 已知工程限制

- 标准 `PointCloud2` 回调会把所有点的 `curvature` 初始化为零；若输入没有逐点时间，扫描去畸变不能正确发挥作用。
- `lio_node` 的无 IMU 兼容路径会跳过正常的 IMU 同步与去畸变假设，不应当作可靠的 LiDAR–IMU 运行模式。
- IESKF 和 ICP 缺少充分的退化检测与鲁棒性保护；部署前应在目标传感器、场景和 rosbag 数据上完成验证。
- `play_bag.sh` 含有机器相关的绝对路径，需要按本机环境修改。

## License

各子包保留其原有 `LICENSE` 文件。使用、修改或再分发前，请分别核对对应模块的许可证和依赖库许可证。
