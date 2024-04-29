#!/usr/bin/env pybricks-micropython

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor, ColorSensor
from pybricks.parameters import Port, Stop, Direction, Color, Button
from pybricks.tools import wait

MAX_BASE_ANGLE = 260        # NOTE: Set the angle to an apropriate value

BASE_MOTOR_SPEED = 60
GRIPPER_MOTOR_SPEED = 200
ELBOW_MOTOR_SPEED = 60

ZONE_ANGLES = [0, 100, 150, 200]

SENSOR_HIGHT = 63
TOP_HIGHT = 77
GROUND_HIGHT = 30
ELEVATED_HEIGHT = 58

BASESWITCH_OFFSET = 7


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
    menu = True
    pickUpIndex = 0
    wait_time = 3000                # Time between periodic checks
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
        self.base_motor.control.limits(speed=BASE_MOTOR_SPEED, acceleration=120)

        self.initGripper()
        self.initElbow()
        self.initBase(base_offset)


    def initGripper(self):
        # Initialize gripper with closed grip as 0 degrees
        self.gripper_motor.run_until_stalled(GRIPPER_MOTOR_SPEED, then=Stop.COAST, duty_limit=50)
        self.gripper_motor.reset_angle(0)
        self.gripper_motor.run_target(GRIPPER_MOTOR_SPEED, -90, then=Stop.COAST)      # Leave the gripper open

    def initElbow(self):
        # Initialize the elbow motor
        self.elbow_motor.run_until_stalled(-ELBOW_MOTOR_SPEED, then=Stop.HOLD, duty_limit=20)
        self.elbow_motor.reset_angle(0)
        self.elbow_motor.run_target(ELBOW_MOTOR_SPEED, self.top_hight, then=Stop.HOLD)

    def initBase(self, switch_offset):
        # Initialize base motot to where the switch is pressed with an offset
        self.base_motor.run(-BASE_MOTOR_SPEED)
        while not self.base_switch.pressed():
            wait(10)
        self.base_motor.reset_angle(0)
        self.base_motor.run_target(BASE_MOTOR_SPEED, switch_offset, then=Stop.COAST)
        self.base_motor.reset_angle(0)


    def runMotor(self, motor, speed, target, stop_action=Stop.HOLD):
        print(8)
        print(self.ev3.buttons.pressed())
        motor.run_target(speed, target, then=stop_action, wait=False)
        print(9)

        while not(motor.angle() < target + 5 and motor.angle() > target -5):
            wait(50)
            if Button.CENTER in self.ev3.buttons.pressed():
                motor.hold()
                wait(DEBOUNCE_TIME)
                while True:
                    # FIX:: Draw instructions here, Maybe put the motor on coast
                    print(90)
                    button_press = self.ev3.buttons.pressed()
                    if Button.DOWN in button_press:
                        wait(DEBOUNCE_TIME)
                        self.menu = True
                    if Button.CENTER in button_press:
                        wait(DEBOUNCE_TIME)
                        self.runMotor(motor, speed, target, stop_action)
                        return
                    wait(50)
        


    def stallMotor(self, motor, speed, target, stop_action=Stop.HOLD):
        # Check:: if it works
        motor.run_target(speed, target, then=stop_action, wait=False)
        while not motor.control.stalled() and not(motor.angle() < target + 5 and motor.angle() > target -5):
            wait(50)
            if Button.CENTER in self.ev3.buttons.pressed():
                # Check:: Should it be hold
                motor.stop() 
                wait(DEBOUNCE_TIME)
                while True:
                    # FIX:: Draw instructions here, Maybe put the motor on coast
                    button_press = self.ev3.buttons.pressed()
                    if Button.DOWN in button_press:
                        wait(DEBOUNCE_TIME)
                        self.menu = True
                    if Button.CENTER in button_press:
                        wait(DEBOUNCE_TIME)
                        self.stallMotor(motor, speed, target, stop_action)
                        return
                    wait(50)
        motor.hold()

    def wait(self, time):
        waited = 0
        while waited < time:
            wait(10)
            waited += 10
            if Button.CENTER in self.ev3.buttons.pressed():
                wait(DEBOUNCE_TIME)
                
                while True:
                    button_press = self.ev3.buttons.pressed()
                    if Button.DOWN in button_press:
                        wait(DEBOUNCE_TIME)
                        self.menu = True
                    if Button.CENTER in button_press:
                        wait(DEBOUNCE_TIME)
                        break



    def openGripper(self):
        if self.elbow_motor.angle() > -86:
            print(7)
            self.runMotor(self.gripper_motor, GRIPPER_MOTOR_SPEED, -86, stop_action=Stop.COAST)        

    def closeGripper(self):
        self.stallMotor(self.gripper_motor, GRIPPER_MOTOR_SPEED, 0)
        if (self.gripper_motor.angle() < -5):
            return True
        return False
    
    def turnBase(self, target):
        '''Turns base motor to target angle if int or to Zone'''
        if isinstance(target, int):
            target_angle = target
        elif isinstance(target, Zone):
            target_angle = target.angle

        if (self.base_motor.angle() != target_angle):
            self.runMotor(self.base_motor, BASE_MOTOR_SPEED, target_angle)

    def moveElbow(self, target = GROUND_HIGHT, sensor = False, top = False):
        if sensor:
            target_hight = self.sensor_hight
        elif top:
            target_hight = self.top_hight
        elif isinstance(target, int):
            target_hight = target
        elif isinstance(target, Zone):
            target_hight = target.hight

        if self.elbow_motor.angle() != target_hight:
            self.runMotor(self.elbow_motor, ELBOW_MOTOR_SPEED, target_hight)

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


        self.moveElbow(sensor=True)
        block_color, block_size = self.getColor()

        if blockPresent:
            self.moveElbow(zone)
            self.openGripper()

        self.moveElbow(top=True)

        return block_color, block_size

    def menuDraw(self, zones):
        self.main_menu = ["Start", "Set Drop Off", "Set Time", "Get Color", "Stop"]
        self.set_dropoff = ["Zone 1: ", "Zone 2: ", "Zone 3: ", "Zone 4: "]
        self.set_color = ["Red", "Green", "Blue", "Yellow", "PICKUP"]
        self.set_time = ["Check: "]
        self.get_color = ["Zone 1", "Zone 2", "Zone 3", "Zone 4"]

        menu_title = ["Main Menu", "Set Dropoff Color", "", "Set Time", "Get Color At"]
        title_offset = 30


        self.menu_items = [self.main_menu, self.set_dropoff, self.set_color, self.set_time, self.get_color]

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
                else:
                    # Highlight the selected item by inverting the colors
                    self.ev3.screen.draw_text(0, index * 20 + title_offset, item, text_color=Color.WHITE, background_color=Color.BLACK)
            else:
                self.ev3.screen.draw_text(0, index * 20 + title_offset, item)
    


    def menuLoop(self, zones):
        self.menu_selection = 0
        self.item_selection = 0
        self.time_check_selection = False # If the time is being changed

        color_index = [
            Color.RED,
            Color.GREEN,
            Color.BLUE,
            Color.YELLOW
        ]

        while(True):
            pressed = self.ev3.buttons.pressed()
            self.menuDraw(zones)

            if Button.DOWN in pressed:
                if not self.time_check_selection:
                    self.item_selection = (self.item_selection + 1) % len(self.menu_items[self.menu_selection])
                else: 
                    self.wait_time -= 1000 if self.wait_time > 999 else 0
                wait(DEBOUNCE_TIME)

            elif Button.UP in pressed:
                if not self.time_check_selection:
                    self.item_selection = (self.item_selection - 1) % len(self.menu_items[self.menu_selection])
                else: 
                    self.wait_time += 1000
                
                wait(DEBOUNCE_TIME)


        
            elif Button.CENTER in pressed:
                # Main menu
                wait(DEBOUNCE_TIME)
                if self.menu_selection == 0:
                    if self.item_selection == 0:    # Select Start
                        wait(DEBOUNCE_TIME)
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
                    self.menu_title_txt = "Set Color For: Zone " + str(self.item_selection)
                    self.menu_selection = 2
                    self.item_selection = 0

                
                # Choose color for zone
                elif self.menu_selection == 2:
                    if self.item_selection == 4:
                        self.pickUpIndex = selected_zone
                    else:
                        zones[selected_zone].color = color_index[self.item_selection]
                    self.menu_selection = 1
                    self.item_selection = selected_zone

                # Set time
                elif self.menu_selection == 3:
                    if self.item_selection == 0:
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
                        wait(DEBOUNCE_TIME)
                

                

        
            elif Button.LEFT in pressed:
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
                wait(DEBOUNCE_TIME)
            else:
                wait(100)
        
        wait(DEBOUNCE_TIME)

def main():
    robot = Robot(BASESWITCH_OFFSET)

    zones = []
    for angle in ZONE_ANGLES:
        zones.append(Zone(angle))

    zones[2].color = Color.BLUE                 # Random default color
    zones[3].color = Color.GREEN                # Random default color

    robot.moveElbow(top=True)
    robot.turnBase(zones[robot.pickUpIndex])    # Place arm over pick up zone


    while True:
        if robot.menu:
            print(1)
            startRobot = robot.menuLoop(zones)
            print(2)
            if not startRobot:
                print(4)
                break
            robot.menu = False

            robot.turnBase(zones[robot.pickUpIndex])
            print(3)
        print(5)
        


        robot.openGripper()
        print(6)

        robot.moveElbow(zones[robot.pickUpIndex])
        print(10)
        block_present = robot.closeGripper()
        print(11)
        if block_present:
            print(12)
            robot.moveElbow(sensor=True)
            print(13)
            block_color, block_size = robot.getColor()
            print(14)
            block_present = False if block_color == None else True

        print()
        robot.moveElbow(top=True)

        if block_present:
            robot.dropOffblock(zones, block_color)
        robot.wait(robot.wait_time)

if __name__== "__main__":
    main() 