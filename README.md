# ROS 2 Robot Battery Management — Learning Project

## About This Project

This repository is a hands-on learning project built to practice **ROS 2 development with Python**. It focuses on communication between ROS 2 nodes, custom interfaces, action clients and servers, services, parameter configuration, and Git version control.

This project is for educational purposes and experimentation. It is not intended for production use.

## Learning Objectives

- Understand ROS 2 nodes, topics, publishers, and subscribers.
- Create and use custom ROS 2 messages and actions.
- Implement an action client and action server.
- Handle action goals, feedback, results, and cancellation.
- Create ROS 2 services using `std_srvs/srv/Trigger`.
- Use node state to control automatic behavior.
- Configure behavior through YAML parameters and launch arguments.
- Build, run, test, and version-control a ROS 2 workspace.

## Implemented Features

### 1. Battery Monitoring

- Publishes robot battery information through the `battery_topic` topic.
- Uses the custom `RobotStatus` message.
- Simulates battery discharge while the robot is not charging.
- Reports whether the battery needs charging.

### 2. Recharge Action Server and Client

- Defines a custom `Recharge` action.
- Uses `recharge_robot_action` as the action name.
- Allows the client to request a target battery level.
- Provides feedback as the battery level increases.
- Returns a result when the recharge operation finishes.
- Validates recharge goals to accept target levels from 0% to 100%.

### 3. Automatic Recharging

- Monitors incoming battery status messages.
- Automatically requests a recharge when the battery reaches the configured low-battery threshold.
- Prevents repeated goal submissions while a recharge request is already active.
- Supports a configurable low-battery threshold.

### 4. Recharge Cancellation

- Provides the `/cancel_recharge` service.
- Requests cancellation of an active recharge action.
- Handles the action server's cancellation response.
- Pauses automatic recharging when the action finishes with a canceled status.

### 5. Resume Automatic Recharging

- Provides the `/resume_recharge` service.
- Clears the automatic-recharge pause flag.
- Allows a later battery message to trigger a new recharge goal when charging is needed.



## Project Structure

```text
newros2_ws/
├── README.md
└── src/
    ├── robot_control/
    │   ├── config/
    │   ├── launch/
    │   ├── robot_control/
    │   │   ├── battery_publisher.py
    │   │   └── recharge_action_client.py
    │   ├── test/
    │   ├── package.xml
    │   ├── setup.py
    │   └── setup.cfg
    └── robot_interfaces/
        ├── action/
        ├── msg/
        ├── srv/
        ├── CMakeLists.txt
        └── package.xml
```

- **`robot_control`** contains the battery publisher, recharge action client, launch configuration, and YAML parameters.
- **`robot_interfaces`** contains the custom ROS 2 action, message, and service interface definitions.
- **`README.md`** documents the project and its learning objectives.

## Requirements

- Ubuntu Linux
- ROS 2 Jazzy
- Python 3
- `colcon`
- Git

## Build the Workspace

From the workspace root, source ROS 2 and build the packages:

```bash
source /opt/ros/jazzy/setup.bash
cd ~/newros2_ws
colcon build --symlink-install
source install/setup.bash
```

## Run the Robot System

Launch the system with a low-battery threshold of 10%:

```bash
ros2 launch robot_control robot_system.launch.py low_battery_threshold:=10
```

The battery publisher and recharge action client should start. When the battery reaches the configured threshold, the client can automatically request recharging.

## Available Services

### Cancel an Active Recharge

```bash
ros2 service call /cancel_recharge std_srvs/srv/Trigger "{}"
```

The service submits a cancellation request. The action server's response determines whether cancellation is accepted.

### Resume Automatic Recharging

```bash
ros2 service call /resume_recharge std_srvs/srv/Trigger "{}"
```

This re-enables automatic recharging. A new recharge goal is triggered when a subsequent battery message satisfies the low-battery condition.

## Current Scope and Limitations

- Battery behavior is simulated; this project does not control physical robot hardware.
- The project is being developed incrementally as part of a personal learning journey.
- Testing so far has focused on the battery lifecycle, automatic recharge, action feedback and results, cancellation, and resume behavior.
- Further improvements and additional tests may be added as learning progresses.

## Purpose

The primary goal is to learn ROS 2 by building, testing, debugging, and improving a working project rather than only following tutorials.

**Status:** Ongoing learning project.
