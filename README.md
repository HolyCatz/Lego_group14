# PA1473 - Software Development: Agile Project (Template)

## Introduction

This project is a Python script designed for controlling a robotic arm using the pybricks-micropython library on an EV3 Brick. The script allows the robot to perform various tasks such as picking up, sorting, and dropping off objects based on their color and size.

## Getting started

To set up the project and install the dependencies, follow these steps:
1. Ensure you have an EV3 Brick with the pybricks-micropython firmware installed.
2. Clone this repository to your local machine.
3. Connect your EV3 Brick to your computer via USB.
4. Upload and run the Python script (`main.py`) to your EV3 Brick.


## Building and running

To run the project, follow these steps:
1. Ensure the EV3 Brick is powered on and the script is uploaded.
2. Press the center button on the EV3 Brick to start the script.
3. Follow the on-screen instructions to navigate the menu and control the robotic arm.
4. Press and hold the center button to pause the script or trigger an emergency stop.

The script accepts various arguments to control the behavior of the robotic arm, such as setting drop-off zones, adjusting time intervals, and retrieving color information.

## Features

The following user stories have been implemented in this project:
- [x] US01: As a customer, I want the robot to pick up items from a designated position.
- [x] US02: As a customer, I want the robot to drop items off at a designated position.
- [x] US03: As a customer, I want the robot to be able to determine if an item is present at a given location.
- [x] US04: As a customer, I want the robot to tell me the color and shape of an item at a designated position.
- [x] US05: As a customer, I want the robot to drop items off at different locations based on the color of the item.
- [x] US06: As a customer, I want the robot to be able to pick up items from elevated positions.
- [x] US07/08: As a customer, I want to be able to calibrate a maximum of three different colors and assign them to specific drop-off zones.
- [x] US09: As a customer, I want the robot to check the pickup location periodically to see if a new item has arrived.
- [ ] US10: As a customer, I want the robots to sort items at a specific time.
- [ ] US11: As a customer, I want two robots (from two teams) to communicate and work together on items sorting without colliding with each other.
- [ ] US12: As a customer, I want to be able to manually set the locations and heights of one pick-up zone and two drop-off zones. (Implemented either by manually dragging the arm to a position or using buttons).
- [x] US13: As a customer, I want to easily reprogram the pickup and drop off zone of the robot.
- [x] US14: As a customer, I want to easily change the schedule of the robot pick up task.
- [x] US15: As a customer, I want to have an emergency stop button, that immediately terminates the operation of the robot safely.
- [ ] US16: As a customer, I want the robot to be able to pick an item up and put it in the designated drop-off location within 5 seconds.
- [ ] US17: As a customer, I want the robot to pick up items from a rolling belt and put them in the designated positions based on color and shape.
- [x] US18: As a customer, I want to have a pause button that pauses the robot's operation when the button is pushed and then resumes the program from the same point when I push the button again.
- [ ] US19: As a customer, I want a very nice dashboard to configure the robot program and start some tasks on demand.
