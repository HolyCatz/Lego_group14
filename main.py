#!/usr/bin/env pybricks-micropython

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor, ColorSensor
from pybricks.parameters import Port, Stop, Direction, Color, Button
from pybricks.tools import wait


MAX_BASE_ANGLE = 260        # NOTE: Set the angle to an apropriate value

BASE_MOTOR_SPEED = 60
GRIPPER_MOTOR_SPEED = 200
ELBOW_MOTOR_SPEED = 60

SENSOR_HIGHT = 58
GROUND_HIGHT = 30
ELEVATED_HEIGHT = 55

BASESWITCH_OFFSET = 7

DROP_OFF1   = 100
DROP_OFF2   = 150
DROP_OFF3   = 200
PICKUP      = 0

PICKUP_ELEVATED = False

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
        return "Error"

class Robot:
    
    #region Initialize Robot

    def __init__(self, elbow_end, base_offset) -> None:
        self.ev3 = EV3Brick()
        self.gripper_motor = Motor(Port.A)
        self.elbow_motor = Motor(Port.B, Direction.COUNTERCLOCKWISE, [8, 40])
        self.base_motor = Motor(Port.C, Direction.COUNTERCLOCKWISE, [12, 36])

        self.base_switch = TouchSensor(Port.S1)
        self.elbow_sensor = ColorSensor(Port.S2)
        self.elbow_motor.control.limits(speed=ELBOW_MOTOR_SPEED, acceleration=120)
        self.base_motor.control.limits(speed=BASE_MOTOR_SPEED, acceleration=120)

        self.wait_time = 3000            # NEW:: Time between knowing a block is not present and checking again

        self.initGripper()
        self.initElbow(elbow_end)
        self.initBase(base_offset)


        self.pickUp = PICKUP
        self.dropOffAngle = [DROP_OFF1, DROP_OFF2, DROP_OFF3]
        self.dropOffColor = [Color.BLUE, Color.RED, Color.GREEN]


    def initGripper(self):
        # Initialize gripper with closed grip as 0 degrees
        self.gripper_motor.run_until_stalled(GRIPPER_MOTOR_SPEED, then=Stop.COAST, duty_limit=50)
        self.gripper_motor.reset_angle(0)
        self.gripper_motor.run_target(GRIPPER_MOTOR_SPEED, -90, then=Stop.COAST)      # Leave the gripper open

    def initElbow(self, end_angle):
        # Initialize the elbow motor
        self.elbow_motor.run_until_stalled(-ELBOW_MOTOR_SPEED, then=Stop.HOLD, duty_limit=20)
        self.elbow_motor.reset_angle(0)
        self.elbow_motor.run_target(ELBOW_MOTOR_SPEED, end_angle, then=Stop.HOLD)

    def initBase(self, switch_offset):
        # Initialize base motot to where the switch is pressed with an offset
        self.base_motor.run(-BASE_MOTOR_SPEED)
        while not self.base_switch.pressed():
            wait(10)
        self.base_motor.reset_angle(0)
        self.base_motor.run_target(BASE_MOTOR_SPEED, switch_offset, then=Stop.COAST)
        self.base_motor.reset_angle(0)

    # endregion

    def openGripper(self):
        if self.elbow_motor.angle() > -90:
            self.gripper_motor.run_target(GRIPPER_MOTOR_SPEED, -90, then=Stop.COAST)

    def closeGripper(self):
        # Close the gripper untill motor stalls and holds it there
        self.gripper_motor.run_until_stalled(GRIPPER_MOTOR_SPEED, then=Stop.HOLD, duty_limit=45)

        if (self.gripper_motor.angle() < -5):
            return True
        else:
            return False
    
    
    def turnBase(self, angle):
        # Turn the base to a desired angle and hold
        if (angle >= 0 and angle <= MAX_BASE_ANGLE):  # Only let the Base turn within safe range
            self.base_motor.run_target(BASE_MOTOR_SPEED, angle, then=Stop.HOLD)

   
    def elbowUp(self):
        # if self.elbow_motor.angle() < SENSOR_HIGHT:
        self.elbow_motor.run_target(ELBOW_MOTOR_SPEED, SENSOR_HIGHT, then=Stop.HOLD) 

    def elbowDown(self, elevated=False):
        if elevated:
            self.elbow_motor.run_target(ELBOW_MOTOR_SPEED, ELEVATED_HEIGHT, then=Stop.HOLD)
        else:
            self.elbow_motor.run_target(ELBOW_MOTOR_SPEED, GROUND_HIGHT, then=Stop.HOLD)
    

    def goToPickUp(self):
        self.turnBase(self.pickUp)

    def goToDropOff(self, index):
        self.turnBase(self.dropOffAngle[index])

    def dropBlock(self, elevated=False):
        self.elbowDown(elevated)
        self.openGripper()
        self.elbowUp()


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


    def pickUpBlock(self):
        self.elbowUp()
        self.goToPickUp()
        self.openGripper()

        self.elbowDown(PICKUP_ELEVATED)
        blockPresent = self.closeGripper()
        self.elbowUp()

        if blockPresent:
            color, size = self.getColor()
            print("Color: ", formatColor(color), ", Size: ", size)
        else:
            color = None

        wait(100) # NOTE:: Not sure if needed
        if (self.gripper_motor.angle() > -10 or color == None):
            blockPresent = False
        else:
            blockPresent = True   

        return blockPresent, color


    def dropOffAtColor(self, color):
        if color in self.dropOffColor:
            self.goToDropOff(self.dropOffColor.index(color))
            blockColor = self.elbow_sensor.color()  # NEW:: check for dropped block
            if (blockColor != None):
                self.dropBlock()
            return True
        return False
    

    def getSizeColorAt(self, index):
        color = None
        size = "UNKNOWN"
        index -= 1
        
        self.openGripper()
        
        if index < 0:
            self.goToPickUp()
            self.elbowDown(PICKUP_ELEVATED)
        else:
            self.goToDropOff(index)
            self.elbowDown()

        blockPresent = self.closeGripper()
        self.elbowUp()

        if blockPresent:
            color, size = self.getColor()
            if index < 0:
                self.dropBlock(PICKUP_ELEVATED)
            else:
                self.dropBlock()

        if color == None:
            color = None 
        
        return color, size
        


        

    def menuDraw(self):
        self.main_menu = ["Start", "Set Drop Off", "Set Time", "Get Color", "Stop"]
        self.set_dropoff = ["Zone 1: ", "Zone 2: ", "Zone 3: "]
        self.set_color = ["Red", "Green", "Blue", "Yellow"]
        self.set_time = ["Check: "]
        self.get_color = ["Pick up", "Zone 1", "Zone 2", "Zone 3"]

        menu_title = ["Main Menu", "Set Dropoff Color", "", "Set Time", "Get Color At"]


        self.menu_items = [self.main_menu, self.set_dropoff, self.set_color, self.set_time, self.get_color]

        self.ev3.screen.clear()

        if menu_title[self.menu_selection] != "":
            self.ev3.screen.draw_text(0,0, menu_title[self.menu_selection])
        else:
            self.ev3.screen.draw_text(0,0, self.menu_title_txt)


        for index, item in enumerate(self.menu_items[self.menu_selection]):
            if (self.menu_selection == 1):
                item += formatColor(self.dropOffColor[index])


            if index == self.item_selection:
                if (self.menu_selection == 3) and index == 0:

                    self.ev3.screen.draw_text(0, index * 20 + 30, item, text_color=Color.WHITE if not self.time_check_selection else Color.BLACK, background_color=Color.BLACK if not self.time_check_selection else Color.WHITE)
                    whiteBack = str(int(self.wait_time/1000)) + " s"
                    self.ev3.screen.draw_text(len(item)*12, index * 20 + 30, whiteBack, text_color=Color.BLACK if not self.time_check_selection else Color.WHITE, background_color=Color.WHITE if not self.time_check_selection else Color.BLACK)
                    #print white back with wite background on same line after item
                else:
                    # Highlight the selected item by inverting the colors
                    self.ev3.screen.draw_text(0, index * 20 + 30, item, text_color=Color.WHITE, background_color=Color.BLACK)
            else:
                self.ev3.screen.draw_text(0, index * 20 + 30, item)
    
    
    def menuLoop(self):
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
            self.menuDraw()

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
                if self.menu_selection == 0:
                    if self.item_selection == 0:    # Select Start
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
                    self.dropOffColor[selected_zone] = color_index[self.item_selection]
                    self.menu_selection = 1
                    self.item_selection = selected_zone

                # Set time
                elif self.menu_selection == 3:
                    if self.item_selection == 0:
                        self.time_check_selection = not self.time_check_selection


                elif self.menu_selection == 4:
                    block_color, block_size = self.getSizeColorAt(self.item_selection)
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


def main():
    robot = Robot(SENSOR_HIGHT, BASESWITCH_OFFSET)

    openMenu = True
    
    while True:
        if openMenu:
            startRobot = robot.menuLoop()
            if not startRobot:
                break
            openMenu = False

        blockPresent, color = robot.pickUpBlock()

        wait(100) # NOTE:: Not sure if needed

        buttonPress = robot.ev3.buttons.pressed()
        if Button.LEFT in buttonPress:
            openMenu = True

        if blockPresent:
            blockPresent = not robot.dropOffAtColor(color)

        if (blockPresent and robot.elbow_sensor.color() != None):
            # Block color does not match any of the drop off zones
            wait(500)
            robot.dropBlock(PICKUP_ELEVATED)

        # NOTE: Should move to pickup before the wait

        buttonPress = robot.ev3.buttons.pressed()
        if Button.LEFT in buttonPress:
            openMenu = True

        wait(robot.wait_time)



if __name__== "__main__":
    main() 
