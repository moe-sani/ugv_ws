# ugv_auto_drive — Install & Run

Quick instructions to build and run `ugv_auto_drive` inside the project's Docker (ROS 2 is installed inside the container).

**Prerequisite**
- Be inside the workspace container where ROS 2 and `colcon` are available.

**Build**
Run these from the workspace root inside the docker:

```bash
cd /home/ws/ugv_ws
colcon build --packages-select ugv_auto_drive
source install/setup.bash
```

**Run the node**
After sourcing the install overlay run:

```bash
ros2 pkg executables ugv_auto_drive    # list registered executables
ros2 run ugv_auto_drive auto_drive     # run the auto drive script
```

**What I changed / Why this was needed**
- The package defines a `console_scripts` entry point (`auto_drive = ugv_auto_drive.auto_drive:main`) in `setup.py`.
- Some setuptools installations place generated scripts under `bin/` which `ros2 run` does not scan. I added a `setup.cfg` so scripts are installed under `lib/ugv_auto_drive`, matching other ROS 2 Python packages. Rebuilding is required for the change to take effect.

**Quick checks / troubleshooting**
- Verify the installed script location:

```bash
ls install/ugv_auto_drive/lib/ugv_auto_drive || ls install/ugv_auto_drive/bin
ros2 pkg executables ugv_auto_drive
```

- If `ros2 run` still reports "No executable found":
  - Ensure you ran `source install/setup.bash` in the same shell.
  - Rebuild with `colcon build --packages-select ugv_auto_drive --symlink-install` and source again.

**Notes**
- Run all commands inside the docker where ROS 2 is installed.
- The package entry point uses `rclpy`; ensure `rclpy` is available in the container (it is a declared `exec_depend`).
