#!/usr/bin/env pybricks-micropython

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor, ColorSensor
from pybricks.parameters import Port, Stop, Direction, Color, Button
from pybricks.tools import wait

MAX_BASE_ANGLE = 260        # NOTE: Set the angle to an apropriate value

BASE_MOTOR_SPEED = 150
GRIPPER_MOTOR_SPEED = 200
ELBOW_MOTOR_SPEED = 60

ZONE_ANGLES = [0, 100, 150, 200]

SENSOR_HIGHT = 63
TOP_HIGHT = 77
GROUND_HIGHT = 30
ELEVATED_HEIGHT = 58

BASESWITCH_OFFSET = 15


DEBOUNCE_TIME = 300         # Wait time after a button press so it only get's registered once


def formatColor(color):
    '''Takes in a Color obj or String and retruns the oposite type.'''
    if isinstance(color, str):
        try:
            return getattr(Color, color.upper())
        except AttributeError:
            return None
    elif isinstance(color, Color):
        # Getting the name of the color from a Color object.
        if color == Color.RED:
            txt = "Red"
        elif color == Color.BLUE:
            txt = "Blue"
        elif color == Color.GREEN:
            txt = "Green"
        elif color == Color.YELLOW:
            txt = "Yellow"
        elif color == Color.BROWN:
            txt = "Brown"
        elif color == Color.BLACK:
            txt = "Black"
        elif color == Color.WHITE:
            txt = "White"
        elif color == Color.ORANGE:
            txt = "Orange"
        elif color == Color.PURPLE:
            txt = "Purple"
        else:
            txt = "Unknown"
        return txt
    else:
        return "Unknown"


class Zone:
    hight = GROUND_HIGHT
    color = Color.RED

    def __init__(self, _angle):
        self.angle = _angle

class Robot:
    inEmergency = False
    afterEmergency = False
    menu = True
    pickUpIndex = 0
    wait_time = 3000                # Time between periodic checks
    time_to_start = 0
    sensor_hight = SENSOR_HIGHT     
    top_hight = TOP_HIGHT           # Hight of claw so it doesn't hit elevated objects

    # region Initialize

    def __init__(self, base_offset) -> None:
        self.ev3 = EV3Brick()
        self.gripper_motor = Motor(Port.A)
        self.elbow_motor = Motor(Port.B, Direction.COUNTERCLOCKWISE, [8, 40])
        self.base_motor = Motor(Port.C, Direction.COUNTERCLOCKWISE, [12, 36])

        self.base_switch = TouchSensor(Port.S1)
        self.elbow_sensor = ColorSensor(Port.S2)
        self.elbow_motor.control.limits(speed=ELBOW_MOTOR_SPEED, acceleration=120)
        self.base_motor.control.limits(speed=BASE_MOTOR_SPEED, acceleration=200)

        self.initGripper()
        self.initElbow()
        self.initBase(base_offset)


    def initGripper(self):
        # Initialize gripper with closed grip as 0 degrees
        self.gripper_motor.run_until_stalled(GRIPPER_MOTOR_SPEED, then=Stop.COAST, duty_limit=50)
        self.gripper_motor.reset_angle(0)
        self.gripper_motor.run_target(GRIPPER_MOTOR_SPEED, -90, then=Stop.COAST)      # Leave the gripper open
        self.gripper_motor.control.stall_tolerances(50,10)

    def initElbow(self):
        # Initialize the elbow motor
        self.elbow_motor.run_until_stalled(-ELBOW_MOTOR_SPEED, then=Stop.HOLD, duty_limit=20)
        self.elbow_motor.reset_angle(0)
        self.elbow_motor.run_target(ELBOW_MOTOR_SPEED, self.top_hight, then=Stop.HOLD)

    def initBase(self, switch_offset):
        # Initialize base motot to where the switch is pressed with an offset
        self.base_motor.run(-BASE_MOTOR_SPEED/2)
        while not self.base_switch.pressed():
            wait(10)
        self.base_motor.reset_angle(0)
        self.base_motor.run_target(BASE_MOTOR_SPEED, switch_offset, then=Stop.COAST)
        self.base_motor.reset_angle(0)


    def runMotor(self, motor, speed, target, stop_action=Stop.HOLD):
        motor.stop()
        if not self.afterEmergency:
            motor.run_target(speed, target, then=stop_action, wait=False)
            while not(motor.angle() < target + 5 and motor.angle() > target -5):
                wait(50)
                if Button.CENTER in self.ev3.buttons.pressed() and not self.inEmergency:
                    motor.hold()
                    hold_time = 0
                    while Button.CENTER in self.ev3.buttons.pressed() and hold_time < 2000:
                        wait(50)
                        hold_time += 50

                    
                    if hold_time >= 2000:
                        self.emergencyStop()
                        return
                    else:
                        self.pauseMenu()
                        wait(DEBOUNCE_TIME)
                        while True:
                            button_press = self.ev3.buttons.pressed()
                            if Button.DOWN in button_press:
                                wait(DEBOUNCE_TIME)
                                self.menu = True
                            if Button.CENTER in button_press:
                                wait(DEBOUNCE_TIME)
                                self.runtimeDisplay(color=self.current_color, size=self.current_size)
                                self.runMotor(motor, speed, target, stop_action)
                                return
                            wait(50)
        


    def stallMotor(self, motor, speed, target, stop_action=Stop.HOLD):
        motor.stop()
        if not self.afterEmergency:
            print(self.gripper_motor.control.stall_tolerances())
            motor.run_target(speed, target, then=stop_action, wait=False)
            while not motor.control.stalled() and not(motor.angle() < target + 5 and motor.angle() > target -5):
                wait(50)
                if Button.CENTER in self.ev3.buttons.pressed():
                    motor.stop()

                    hold_time = 0
                    while Button.CENTER in self.ev3.buttons.pressed() and hold_time < 2000:
                        wait(50)
                        hold_time += 50

                    
                    if hold_time >= 2000:
                        self.emergencyStop()
                        return
                    else:
                        self.pauseMenu()
                        wait(DEBOUNCE_TIME)
                        while True:
                            # FIX:: Draw instructions here, Maybe put the motor on coast
                            button_press = self.ev3.buttons.pressed()
                            if Button.DOWN in button_press:
                                wait(DEBOUNCE_TIME)
                                self.menu = True
                            if Button.CENTER in button_press:
                                wait(DEBOUNCE_TIME)
                                self.runtimeDisplay(color=self.current_color, size=self.current_size)
                                self.stallMotor(motor, speed, target, stop_action)
                                return
                            wait(50)
            motor.hold()


    def pauseMenu(self):
        self.ev3.screen.clear()
        self.ev3.screen.draw_text(0, 0, "Paused")
        self.ev3.screen.draw_text(0, 50, "To Resume")
        self.ev3.screen.draw_text(0, 70, "Press Center")

    def closestZone(self):
        current = self.base_motor.angle()
        return min(range(len(ZONE_ANGLES)), key=lambda i: abs(ZONE_ANGLES[i] - current))
            

    def emergencyStop(self):
        self.inEmergency = True
        self.ev3.screen.clear()
        self.ev3.screen.draw_text(0, 30, "Emergency")
        closest_zone = self.closestZone()
        self.ev3.screen.draw_text(0, 50, "Going to")
        self.ev3.screen.draw_text(0, 70, "Zone: " + str(closest_zone))

        self.moveElbow(top=True, speed=ELBOW_MOTOR_SPEED/4)
        self.turnBase(self.backupZones[closest_zone], speed=BASE_MOTOR_SPEED/4)
        self.moveElbow(self.backupZones[closest_zone], speed=ELBOW_MOTOR_SPEED/4)
        self.openGripper()
        self.menu = True
        self.inEmergency = False
        self.afterEmergency = True



    def wait(self, time):
        waited = 0
        while waited < time:
            wait(10)
            waited += 10
            if Button.CENTER in self.ev3.buttons.pressed():
                wait(DEBOUNCE_TIME)
                self.menu = True
                break
                while True:
                    button_press = self.ev3.buttons.pressed()
                    if Button.DOWN in button_press:
                        wait(DEBOUNCE_TIME)
                        self.menu = True
                    if Button.CENTER in button_press:
                        wait(DEBOUNCE_TIME)
                        break



    def openGripper(self):
        print("open1")
        if self.elbow_motor.angle() > -86:
            self.runMotor(self.gripper_motor, GRIPPER_MOTOR_SPEED, -86, stop_action=Stop.COAST)        
        print("open2")

    def closeGripper(self):
        self.stallMotor(self.gripper_motor, GRIPPER_MOTOR_SPEED, 0)
        print(self.gripper_motor.angle())
        if (self.gripper_motor.angle() < -5):
            return True
        return False
    
    def turnBase(self, target, speed=BASE_MOTOR_SPEED):
        '''Turns base motor to target angle if int or to Zone'''
        if isinstance(target, int):
            target_angle = target
        elif isinstance(target, Zone):
            target_angle = target.angle

        if (self.base_motor.angle() != target_angle):
            self.runMotor(self.base_motor, speed, target_angle)

    def moveElbow(self, target = GROUND_HIGHT, sensor = False, top = False, speed=ELBOW_MOTOR_SPEED):
        if sensor:
            target_hight = self.sensor_hight
        elif top:
            target_hight = self.top_hight
        elif isinstance(target, int):
            target_hight = target
        elif isinstance(target, Zone):
            target_hight = target.hight

        if self.elbow_motor.angle() != target_hight:
            self.runMotor(self.elbow_motor, speed, target_hight)

    def getColor(self):
        size = "SMALL"
        color = self.elbow_sensor.color()
        brickSize = self.elbow_sensor.reflection()

        if color == None:
            return color, "UNKNOWN"

        if color == Color.RED:
            if brickSize > 50:
                size = "BIG"
        elif color == Color.GREEN or color == Color.BLUE or color == Color.BLACK:
            if brickSize > 9:
                size = "BIG"
            colorTest = self.elbow_sensor.rgb()
            if colorTest[2] > colorTest[1]:
                color = Color.BLUE
            else:
                color = Color.GREEN
            
        elif color == Color.YELLOW or color == Color.BROWN:
            color = Color.YELLOW
            if brickSize > 50:
                size = "BIG"
        else:
            size = "UNKNOWN"
        return color, size

    def dropOffblock(self, zones, color):
        '''Drops off block at corresponding zone or puts it back down in pick up zone.'''
        found_zone = False
        for i, zone in enumerate(zones): 
            if i != self.pickUpIndex and zone.color == color:            
                self.turnBase(zone)
                self.moveElbow(zone)
                self.openGripper()
                self.moveElbow(top=True)
                self.turnBase(zones[self.pickUpIndex])
                found_zone = True
                break
        if not found_zone:
            self.moveElbow(zones[self.pickUpIndex])
            self.openGripper()
            self.moveElbow(top=True)


    def getSizeColorAt(self, zone):
        color = None
        size = "UNKNOWN"

        self.openGripper()
        self.moveElbow(top=True)
        self.turnBase(zone)
        self.moveElbow(zone)

        blockPresent = self.closeGripper()
        print(blockPresent)

        self.moveElbow(sensor=True)
        block_color, block_size = self.getColor()
        if blockPresent:
            self.moveElbow(zone)
            self.openGripper()

        self.moveElbow(top=True)

        return block_color, block_size
    
    def runtimeDisplay(self, color="No Block", size="No Block"):
        self.ev3.screen.clear()
        self.ev3.screen.draw_text(0, 0, "Running")
        self.ev3.screen.draw_text(0, 20, "Emergency: Hold")
        self.ev3.screen.draw_text(0, 40, "Pause: Press")
        self.ev3.screen.draw_text(0, 70, "Color: " + color)
        self.ev3.screen.draw_text(0, 90, "Size: " + size)

        


    def menuDraw(self, zones):
        self.main_menu = ["Start", "Set Drop Off", "Set Time", "Get Color", "Stop"]
        self.set_dropoff = ["Zone 1: ", "Zone 2: ", "Zone 3: ", "Zone 4: "]
        self.set_color = ["Red", "Green", "Blue", "Yellow", "PICKUP"]
        self.set_time = ["Check: ", "Set Time: "]
        self.get_color = ["Zone 1", "Zone 2", "Zone 3", "Zone 4"]
        self.set_hight = ["Elevated", "Ground"]

        menu_title = ["Main Menu", "Set Dropoff Color", "", "Set Time", "Get Color At", ""]
        title_offset = 30


        self.menu_items = [self.main_menu, self.set_dropoff, self.set_color, self.set_time, self.get_color, self.set_hight]

        
        self.ev3.screen.clear()

        title_offset = 30
        if menu_title[self.menu_selection] != "":
            self.ev3.screen.draw_text(0,0, menu_title[self.menu_selection])
        else:
            self.ev3.screen.draw_text(0,0, self.menu_title_txt)


        for index, item in enumerate(self.menu_items[self.menu_selection]):
            if (self.menu_selection == 1):
                if index == self.pickUpIndex:
                    item += "Pickup"
                else:
                    item += formatColor(zones[index].color)


            if index == self.item_selection:
                if (self.menu_selection == 3) and index == 0:

                    self.ev3.screen.draw_text(0, index * 20 + 30, item, text_color=Color.WHITE if not self.time_check_selection else Color.BLACK, background_color=Color.BLACK if not self.time_check_selection else Color.WHITE)
                    whiteBack = str(int(self.wait_time/1000)) + " s"
                    self.ev3.screen.draw_text(len(item)*12, index * 20 + 30, whiteBack, text_color=Color.BLACK if not self.time_check_selection else Color.WHITE, background_color=Color.WHITE if not self.time_check_selection else Color.BLACK)
                    #print white back with wite background on same line after item
                elif (self.menu_selection == 3) and index == 1:
                    self.ev3.screen.draw_text(0, index * 20 + 30, item, text_color=Color.WHITE if not self.time_check_selection else Color.BLACK, background_color=Color.BLACK if not self.time_check_selection else Color.WHITE)
                    whiteBack = str(int(self.time_to_start/60)) + " m" # need to change this
                    self.ev3.screen.draw_text(len(item)*12, index * 20 + 30, whiteBack, text_color=Color.BLACK if not self.time_check_selection else Color.WHITE, background_color=Color.WHITE if not self.time_check_selection else Color.BLACK)
               
                else:
                    # Highlight the selected item by inverting the colors
                    self.ev3.screen.draw_text(0, index * 20 + title_offset, item, text_color=Color.WHITE, background_color=Color.BLACK)
            else:
                self.ev3.screen.draw_text(0, index * 20 + title_offset, item)
    


    def menuLoop(self, zones):
        self.current_color = "No Block"
        self.current_size = "No Block"
        self.menu_selection = 0
        self.item_selection = 0
        self.time_check_selection = False # If the time is being changed

        color_index = [
            Color.RED,
            Color.GREEN,
            Color.BLUE,
            Color.YELLOW
        ]

        needDraw = True     # True if something has changed and screen needs to be redrawn

        while(True):
            pressed = self.ev3.buttons.pressed()
            if needDraw:
                self.menuDraw(zones)
                needDraw = False

            if Button.DOWN in pressed:
                needDraw = True

                if not self.time_check_selection:
                    self.item_selection = (self.item_selection + 1) % len(self.menu_items[self.menu_selection])
                else: 
                    if self.item_selection == 0:
                        self.wait_time -= 1000 if self.wait_time > 999 else 0
                    elif self.item_selection == 1:
                        self.time_to_start -= 60 if self.time_to_start > 59 else 0

            elif Button.UP in pressed:
                needDraw = True
                if not self.time_check_selection:
                    self.item_selection = (self.item_selection - 1) % len(self.menu_items[self.menu_selection])
                else: 
                    if self.item_selection == 0:
                        self.wait_time += 1000
                    if self.item_selection == 1:
                        self.time_to_start += 60



        
            elif Button.CENTER in pressed:
                needDraw = True
                # Main menu
                if self.menu_selection == 0:
                    if self.item_selection == 0:    # Select Start
                        wait(DEBOUNCE_TIME)
                        self.backupZones = zones
                        
                        return True
                    elif self.item_selection == 1:    # Select change color
                        self.menu_selection = 1
                        self.item_selection = 0
                    elif self.item_selection == 2:  # Select change time
                        self.menu_selection = 3
                        self.item_selection = 0
                    elif self.item_selection == 3:  # Get Color
                        self.menu_selection = 4
                        self.item_selection = 0


                    elif self.item_selection == len(self.main_menu) - 1: # Select Last item (Stop)
                        return False


                # Set dropoff color
                elif self.menu_selection == 1:
                    selected_zone = self.item_selection
                    self.menu_title_txt = "Set Color: Zone " + str(selected_zone)
                    self.menu_selection = 2
                    self.item_selection = 0

                
                # Choose color for zone
                elif self.menu_selection == 2:
                    if self.item_selection == 4:
                        self.pickUpIndex = selected_zone
                    else:
                        zones[selected_zone].color = color_index[self.item_selection]
                    
                    self.menu_title_txt = "Set Hight: Zone " + str(selected_zone)
                    self.menu_selection = 5

                    if zones[selected_zone].hight == GROUND_HIGHT:
                        self.item_selection = 1
                    else:
                        self.item_selection = 0
                    

                # Set time
                elif self.menu_selection == 3:
                    if self.item_selection == 0:
                        self.time_check_selection = not self.time_check_selection
                    elif self.item_selection == 1:
                        self.time_check_selection = not self.time_check_selection


                elif self.menu_selection == 4:
                    wait(DEBOUNCE_TIME)
                    block_color, block_size = self.getSizeColorAt(zones[self.item_selection])
                    self.ev3.screen.clear()
                    self.ev3.screen.draw_text(0,0, self.get_color[self.item_selection])
                    self.ev3.screen.draw_text(0, 30, "Color: " + formatColor(block_color))
                    self.ev3.screen.draw_text(0, 20 + 30, "Size: " + block_size)


                    self.ev3.screen.draw_text(0, 90, "Enter")
                    wait(DEBOUNCE_TIME)
                    while(True):
                        temp_pressed = self.ev3.buttons.pressed()
                        if Button.CENTER in temp_pressed:
                            break
                        wait(50)
                    
                elif self.menu_selection == 5:
                    if self.item_selection == 0:
                        zones[selected_zone].hight = ELEVATED_HEIGHT
                    else:
                        zones[selected_zone].hight = GROUND_HIGHT
                    self.menu_selection = 1
                    self.item_selection = selected_zone
                

        
            elif Button.LEFT in pressed:
                needDraw = True
                if self.menu_selection == 1:
                    self.menu_selection = 0
                elif self.menu_selection == 2:
                    self.menu_selection = 1
                elif self.menu_selection == 3:
                    if self.time_check_selection:
                        self.time_check_selection = False
                    else:
                        self.menu_selection = 0
                elif self.menu_selection == 4:
                    self.menu_selection = 0

                self.item_selection = 0
            else:
                wait(50)
        
            if (Button.LEFT in pressed or 
                Button.UP in pressed or 
                Button.DOWN in pressed or 
                Button.CENTER in pressed):
                wait(DEBOUNCE_TIME)


    def drawTimeToStart(self):
        self.ev3.screen.clear()
        self.ev3.screen.draw_text(0, 0, "Waiting to Start")
        self.ev3.screen.draw_text(0, 50, "Starting in: ")
        self.ev3.screen.draw_text(10, 70, str(int(self.time_to_start/60)) + " m " + str(int(self.time_to_start%60)) + " s")

    def dispTimeToStart(self):
        self.drawTimeToStart()
        ms_to_start = self.time_to_start * 1000
        while (ms_to_start > 0):
            wait(6)
            ms_to_start -= 10

            if ms_to_start % 1000 == 0:
                self.time_to_start -= 1 
                self.drawTimeToStart()

            if Button.CENTER in self.ev3.buttons.pressed():
                    wait(DEBOUNCE_TIME)
                    ms_to_start = 0
                    return -1
        
        self.time_to_start = 0
        return 0

            



def main():
    robot = Robot(BASESWITCH_OFFSET)

    zones = []
    for angle in ZONE_ANGLES:
        zones.append(Zone(angle))

    zones[2].color = Color.BLUE                 # Random default color
    zones[3].color = Color.GREEN                # Random default color

    robot.moveElbow(top=True)
    robot.turnBase(zones[robot.pickUpIndex])    # Place arm over pick up zone

    interruptedStart = 0
    while True:
        if robot.menu:
            robot.afterEmergency = False
            startRobot = robot.menuLoop(zones)

            if not startRobot:
                break

            if robot.time_to_start > 0:
                interruptedStart = robot.dispTimeToStart()

            if interruptedStart == -1:
                robot.time_to_start = 0
                robot.menu = True
                robot.afterEmergency = True
            else:
                robot.runtimeDisplay()
                robot.menu = False

            robot.moveElbow(top=True)
            robot.turnBase(zones[robot.pickUpIndex])

        robot.openGripper()

        robot.moveElbow(zones[robot.pickUpIndex])

        block_present = robot.closeGripper()

        if block_present:
            robot.moveElbow(sensor=True)
            block_color, block_size = robot.getColor()
            robot.current_color = formatColor(block_color)
            robot.current_size = block_size
            robot.runtimeDisplay(color=formatColor(block_color), size=block_size)
            block_present = False if block_color == None else True

        robot.moveElbow(top=True)

        if block_present:
            robot.dropOffblock(zones, block_color)
            robot.current_color = "No Block"
            robot.current_size = "No Block"
        
        if not robot.afterEmergency:
            robot.runtimeDisplay()
            robot.wait(robot.wait_time)

if __name__== "__main__":
    main() 
