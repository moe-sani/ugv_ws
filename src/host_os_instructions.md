
# Jetson Host OS Instructions (ROS 2 UGV + Edge Impulse)

This file documents the steps taken to get the Waveshare UGV “basic bringup” working inside `~/ros2_ws`, alongside `edgeimpulse_ros`.

Goal:
- Build and run the robot base drivers and lidar bringup via:
	- `ros2 launch ugv_bringup bringup_lidar.launch.py use_rviz:=false|true`
- Keep the workspace buildable even when the vendor repo contains many extra navigation/visualization stacks.

## Workspace Layout

- Main ROS2 workspace: `~/ros2_ws`
	- Contains `edgeimpulse_ros` and (copied) Waveshare robot packages under:
		- `~/ros2_ws/src/ugv_main/...`
		- `~/ros2_ws/src/ugv_else/...`

Original vendor workspace (reference): `~/ugv_ws/src/...`

## What `bringup_lidar.launch.py` actually needs

The launch file `ugv_bringup/launch/bringup_lidar.launch.py` starts/includes:

- `ugv_bringup` (Python package)
	- Node: `ugv_bringup` (UART feedback: IMU raw, mag, raw wheel odom, voltage)
	- Node: `ugv_driver` (subscribes `cmd_vel`, forwards to UART)
- `ugv_base_node` (C++ package)
	- Node: `base_node` (computes/publishes `odom` and optional TF)
- `ldlidar` (C++ package)
	- Launch include: `ldlidar.launch.py` → picks actual model launch using `LDLIDAR_MODEL`
- `rf2o_laser_odometry` (C++ package)
	- Launch include: `rf2o_laser_odometry.launch.py`
- `ugv_description` (URDF + display launch)
	- Launch include: `display.launch.py` → uses `UGV_MODEL` and (unfortunately) references `ugv_nav` for RViz config paths.

### Environment variables required at runtime

The vendor launch files expect these environment variables:

- `UGV_MODEL`
	- Must match a URDF base name in `ugv_description/urdf/` (e.g. `ugv_rover`, `ugv_beast`, `rasp_rover`).
- `LDLIDAR_MODEL`
	- Must match a launch base name in `ldlidar/launch/` (e.g. `ld06`, `ld19`, `stl27l`).

Example:

```bash
export UGV_MODEL=ugv_rover
export LDLIDAR_MODEL=stl27l
```

## Two build strategies

### Strategy A (recommended): build only the bringup stack

This avoids pulling in Nav2, exploration, web UI, etc.

```bash
cd ~/ros2_ws
source /opt/ros/$ROS_DISTRO/setup.bash

colcon build --symlink-install \
	--packages-select \
	ugv_bringup ugv_base_node ugv_description ldlidar rf2o_laser_odometry edgeimpulse_ros
```

### Strategy B: build “everything” (full vendor repo)

If you want to build everything, you must also install lots of extra dependencies (Nav2 bringup, rosbridge, etc.).

In this chat we ended up installing additional packages so full builds could proceed farther, but ultimately the simplest path for “basic driving” is Strategy A.

## Common build errors and fixes

### 1) `explore_lite` fails: missing `nav2_msgs`

Error:
- `Could not find a package configuration file provided by "nav2_msgs"`

Fix options:
- Option 1 (minimal): don’t build it (`--packages-select ...` or add `COLCON_IGNORE`).
- Option 2 (full stack): install Nav2 components:

```bash
sudo apt update
sudo apt install -y ros-$ROS_DISTRO-nav2-msgs ros-$ROS_DISTRO-nav2-costmap-2d
```

### 2) `vizanti_server` fails: missing `rosbridge_suite`

Error:
- `Could not find a package configuration file provided by "rosbridge_suite"`

Fix options:
- Option 1 (minimal): don’t build it.
- Option 2 (full stack):

```bash
sudo apt update
sudo apt install -y ros-$ROS_DISTRO-rosbridge-suite python3-flask
```

### 3) `ugv_nav` fails: missing `nav2_bringup`

Error:
- `Could not find a package configuration file provided by "nav2_bringup"`

Fix:

```bash
sudo apt update
sudo apt install -y ros-$ROS_DISTRO-nav2-bringup
```

## Why `ugv_nav` was required even for bringup

Even when launching with `use_rviz:=false`, `ugv_description/launch/display.launch.py` looks up the `ugv_nav` package directory to build paths to RViz config files.

So if `ugv_nav` is missing (or ignored and never installed), launch can fail with:

`package 'ugv_nav' not found`

Solutions:
- Install/build `ugv_nav`, OR
- (Alternative approach) adjust the launch file to not depend on `ugv_nav` when RViz is disabled.
	- We did *not* take this route in the chat, since you requested not to edit code.

## Handling extra packages you don’t want to build (COLCON_IGNORE)

`colcon` will skip any package folder containing a file named `COLCON_IGNORE`.

During debugging we used this to ignore optional stacks (Nav2/exploration/web UI) that were blocking the build.

Typical candidates to ignore for “basic driving only”:
- `ugv_main/ugv_nav` (Nav2 bringup)
- `ugv_else/explore_lite` (Nav2 exploration)
- `ugv_else/teb_local_planner` (Nav2)
- `ugv_else/costmap_converter/costmap_converter` (Nav2)
- `ugv_else/vizanti/vizanti_server` (web UI + rosbridge)
- `ugv_else/cartographer` (heavy SLAM deps)

Note: if you ignore `ugv_nav`, you may hit the runtime “package not found” issue above.

## Runtime prerequisites (apt)

These are commonly needed for the bringup + robot model:

```bash
sudo apt update
sudo apt install -y \
	python3-serial \
	ros-$ROS_DISTRO-robot-state-publisher \
	ros-$ROS_DISTRO-joint-state-publisher \
	ros-$ROS_DISTRO-joint-state-publisher-gui \
	ros-$ROS_DISTRO-rviz2
```

## Launch commands

After a successful build:

```bash
cd ~/ros2_ws
source install/setup.bash

export UGV_MODEL=ugv_rover
export LDLIDAR_MODEL=stl27l

ros2 launch ugv_bringup bringup_lidar.launch.py use_rviz:=false
```

To start RViz:

```bash
ros2 launch ugv_bringup bringup_lidar.launch.py use_rviz:=true
```

## Notes

- The “UGV_MODEL missing” exception was fixed by exporting `UGV_MODEL` before launch.
- If you want joystick driving:
	- Install `ros-$ROS_DISTRO-joy` + `ros-$ROS_DISTRO-teleop-twist-joy` and configure it to publish to `cmd_vel`.

