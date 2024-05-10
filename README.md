# PA1473 - Software Development: Agile Project

## Introduction

This project involves a Python script that operates a robotic arm using the pybricks-micropython library on an EV3 Brick. The robotic arm is programmed to execute tasks such as picking up, sorting, and dropping objects based on specific attributes like color.

## Getting started

**Prerequisites:**
- An EV3 Brick with pybricks-micropython firmware.
- A computer with USB port and internet access.

**Setup Instructions:**
1. Clone the project repository to your local machine using `git clone https://github.com/HolyCatz/Lego_group14`.
2. Connect the EV3 Brick to your computer using a USB cable.
3. Transfer the `main.py` script to your EV3 Brick using your preferred IDE that supports EV3 development.

## Building and running

**Running the Program:**
1. Power on the EV3 Brick.
2. Use the center button on the EV3 Brick to launch the script.
3. Utilize the on-screen prompts to operate the robotic arm, navigating through options to select tasks or settings.
4. To stop or pause the script, press and hold the center button. This can be used for emergency stops or pausing the operation.

**Arguments and Controls:**
- The script supports various runtime arguments for customizing operations, such as defining drop-off zones or modifying timing intervals.
- The robotic arm's actions can be fine-tuned in real-time based on the observed outputs and requirements.

## Features

**Implemented User Stories:**
- [x] **US01:** As a customer, I want the robot to pick up items from a designated position.
- [x] **US02:** As a customer, I want the robot to drop items off at a designated position.
- [x] **US03:** As a customer, I want the robot to be able to determine if an item is present at a given location.
- [x] **US04:** As a customer, I want the robot to tell me the color and shape of an item at a designated position.
- [x] **US05:** As a customer, I want the robot to drop items off at different locations based on the color of the item.
- [x] **US06:** As a customer, I want the robot to be able to pick up items from elevated positions.
- [x] **US07/08:** As a customer, I want to be able to calibrate a maximum of three different colors and assign them to specific drop-off zones.
- [x] **US09:** As a customer, I want the robot to check the pickup location periodically to see if a new item has arrived.
- [x] **US10:** As a customer, I want the robots to sort items at a specific time.
- [ ] **US11:** As a customer, I want two robots (from two teams) to communicate and work together on items sorting without colliding with each other.
- [x] **US12:** As a customer, I want to be able to manually set the locations and heights of one pick-up zone and two drop-off zones. (Implemented either by manually dragging the arm to a position or using buttons).
- [x] **US13:** As a customer, I want to easily reprogram the pickup and drop off zone of the robot.
- [x] **US14:** As a customer, I want to easily change the schedule of the robot pick up task.
- [x] **US15:** As a customer, I want to have an emergency stop button, that immediately terminates the operation of the robot safely.
- [x] **US16:** As a customer, I want the robot to be able to pick an item up and put it in the designated drop-off location within 5 seconds.
- [ ] **US17:** As a customer, I want the robot to pick up items from a rolling belt and put them in the designated positions based on color and shape.
- [x] **US18:** As a customer, I want to have a pause button that pauses the robot's operation when the button is pushed and then resumes the program from the same point when I push the button again.
- [ ] **US19:** As a customer, I want a very nice dashboard to configure the robot program and start some tasks on demand.
