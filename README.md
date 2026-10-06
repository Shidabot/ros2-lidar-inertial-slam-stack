# ROS 2 LiDAR-Inertial SLAM Stack

A ROS 2 engineering stack for LiDAR–IMU SLAM, pose-graph optimization, and map-based relocalization.

> **Scope**
>
> This repository currently implements SLAM and localization capabilities. It is **not** a complete autonomous-navigation system: it does not contain goal navigation, global planning, local obstacle avoidance, costmaps, or autonomous motion control.

## Implemented components

### `fastlio2`: real-time LiDAR–IMU odometry and local mapping

- Subscribes to LiDAR point clouds and IMU messages.
- Uses an iterated error-state Kalman filter (IESKF) for state estimation.
- Performs IMU initialization, state propagation, and scan undistortion.
- Updates the state using point-to-plane residuals.
- Maintains an incremental local point-cloud map with ikd-Tree.

Primary outputs:

```text
/fastlio2/lio_odom       nav_msgs/Odometry
/fastlio2/body_cloud     sensor_msgs/PointCloud2
/fastlio2/world_cloud    sensor_msgs/PointCloud2
/fastlio2/lio_path       nav_msgs/Path
TF: lidar → body
```

### `pgo`: loop closure and pose-graph optimization

- Synchronizes the body-frame cloud and odometry produced by `fastlio2`.
- Selects keyframes according to translation and rotation thresholds.
- Searches loop candidates using spatial proximity and temporal separation.
- Verifies loop candidates with ICP.
- Optimizes the pose graph incrementally with GTSAM iSAM2.
- Publishes a globally corrected `map → lidar` transform and loop-closure markers.

Service:

```text
/pgo/save_maps    Save the optimized map, keyframes, and poses.
```

### `localizer`: ICP relocalization against a known map

- Loads an external PCD map.
- Synchronizes the current cloud with LiDAR odometry.
- Runs coarse-to-fine, two-stage ICP alignment.
- Publishes a `map → lidar` transform and a map cloud after successful alignment.

Services:

```text
/localizer/relocalize        Load a map and provide an initial relocalization pose.
/localizer/relocalize_check  Query whether relocalization has completed successfully.
```

### `fastlio2_gazebo`: simulation and manual teleoperation

- Provides Gazebo worlds, a robot URDF, and sensor models.
- `teleop_node.py` publishes `/cmd_vel` from keyboard input.
- In this project, `/cmd_vel` is only for **manual control of the simulated robot**. It is not produced by a planner or an autonomous controller.

## Nodes and data flow

```text
LiDAR + IMU
    │
    ▼
fastlio2/lio_node
    ├── /fastlio2/lio_odom
    ├── /fastlio2/body_cloud ──► pgo/pgo_node
    │                                ├── loop closure
    │                                ├── GTSAM optimization
    │                                └── TF: map → lidar
    │
    └── /fastlio2/body_cloud ──► localizer/localizer_node
                                     ├── PCD map + ICP
                                     └── TF: map → lidar
```

`pgo` and `localizer` are alternative global-localization paths. The former performs online global correction during mapping; the latter aligns live data against an existing map. They should not normally publish the same `map → lidar` transform at the same time.

## Navigation capabilities not implemented

The following items may appear in early design notes, but there are no corresponding ROS 2 packages, nodes, or algorithm implementations in the current repository:

- Goal interface and navigation state machine.
- Global planning: A*, Dijkstra, RRT*, or equivalent.
- Local planning: DWA, TEB, or trajectory optimization.
- 2D/3D costmaps and real-time obstacle layers.
- Dynamic-obstacle tracking, prediction, and avoidance.
- PID/MPC trajectory tracking and autonomous `/cmd_vel` publication.
- Nav2 integration.

The current system is therefore best described as:

```text
ROS 2 LiDAR–IMU SLAM + pose-graph optimization + ICP relocalization + Gazebo manual teleoperation
```

It is not:

```text
Goal → automatic path planning → dynamic obstacle avoidance → autonomous arrival
```

## Dependencies

- ROS 2 (`rclcpp`, Python launch files, and ROS 2 message interfaces).
- PCL, Eigen, Sophus, and yaml-cpp.
- `livox_ros_driver2`.
- GTSAM for the `pgo` package.
- Gazebo ROS for the simulation package.

## Launch

Build the ROS 2 workspace first, then launch one workflow at a time:

```bash
ros2 launch fastlio2 lio_launch.py
ros2 launch pgo pgo_launch.py
ros2 launch localizer localizer_launch.py
ros2 launch fastlio2_gazebo fastlio_gazebo.launch.py
```

Both `pgo_launch.py` and `localizer_launch.py` start `fastlio2/lio_node`. Do not launch them together unless duplicate nodes, topics, and TF publications have been handled explicitly.

## Configuration

- `fastlio2/config/lio.yaml`: LiDAR/IMU topics, extrinsics, noise, filter resolution, and IESKF settings.
- `pgo/config/pgo.yaml`: keyframe thresholds, loop-search radius, ICP score threshold, and submap parameters.
- `localizer/config/localizer.yaml`: coarse/fine ICP resolution, iteration limits, and matching-score thresholds.

## Engineering limitations

- The standard `PointCloud2` callback initializes every point's `curvature` to zero. If the input lacks per-point time, scan undistortion cannot function correctly.
- The IMU-free compatibility path in `lio_node` bypasses normal IMU synchronization and undistortion assumptions; it should not be treated as a reliable LiDAR–IMU operating mode.
- The IESKF and ICP paths lack comprehensive degeneracy detection and robust outlier handling. Validate them on the target sensors, scenes, and rosbag data before deployment.
- `play_bag.sh` contains a machine-specific absolute path and must be adapted for the local environment.

## License

Each subpackage retains its own `LICENSE` file. Review the license of each module and dependency before use, modification, or redistribution.
