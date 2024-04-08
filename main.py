#!/usr/bin/env pybricks-micropython

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor, ColorSensor
from pybricks.parameters import Port, Stop, Direction, Color, Button
from pybricks.tools import wait

MAX_BASE_ANGLE = 260        # NOTE: Set the angle to an apropriate value

BASE_MOTOR_SPEED = 60
GRIPPER_MOTOR_SPEED = 200
ELBOW_MOTOR_SPEED = 60

SENSOR_HIGHT = 67
GROUND_HIGHT = 30
ELEVATED_HEIGHT = 58

BASESWITCH_OFFSET = 7

DROP_OFF1   = 100
DROP_OFF2   = 150
DROP_OFF3   = 200
PICKUP      = 0


class Robot:

    # region Constructor
    def __init__(self, elbow_end, base_offset) -> None:
        # Initialize the EV3 Brick
        self.ev3 = EV3Brick()
        self.gripper_motor = Motor(Port.A)
        self.elbow_motor = Motor(Port.B, Direction.COUNTERCLOCKWISE, [8, 40])
        self.base_motor = Motor(Port.C, Direction.COUNTERCLOCKWISE, [12, 36])

        self.base_switch = TouchSensor(Port.S1)
        self.elbow_sensor = ColorSensor(Port.S2)
        self.elbow_motor.control.limits(speed=ELBOW_MOTOR_SPEED, acceleration=120)
        self.base_motor.control.limits(speed=BASE_MOTOR_SPEED, acceleration=120)

        self.initGripper()
        self.initElbow(elbow_end)
        self.initBase(base_offset)

        self.dropOffAngle = [DROP_OFF1,DROP_OFF2,DROP_OFF3]
        self.dropOffColor = [Color.BLUE, Color.RED, Color.GREEN]
        self.pickUp = PICKUP
    #endregion

   # region INIT
    
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



# region drawColor(color)
    def drawColor(self, color):
        if color == Color.RED:
            self.drawCenteredText("Color: Red")
        elif color == Color.BLUE:
            self.drawCenteredText("Color: Blue")
        elif color == Color.GREEN:
            self.drawCenteredText("Color: Green")
        elif color == Color.YELLOW:
            self.drawCenteredText("Color: Yellow")
        elif color == Color.BROWN:
            self.drawCenteredText("Color: Brown")
        elif color == Color.BLACK:
            self.drawCenteredText("Color: Black")
        elif color == Color.WHITE:
            self.drawCenteredText("Color: White")
        elif color == Color.ORANGE:
            self.drawCenteredText("Color: Orange")
        elif color == Color.PURPLE:
            self.drawCenteredText("Color: Purple")
        else:
            self.drawCenteredText("Color: Unknown")

# endregion
    
# region drawCenteredText(txt)
    def drawCenteredText(self, txt):
        self.ev3.screen.clear()
        
        height = self.ev3.screen.height
        height = (height // 2) - 10
        self.ev3.screen.draw_text(10, height, txt)
# endregion





# region turnBase(angle)
    def turnBase(self, angle):
        # Turn the base to a desired angle and hold
        # Only let the Base turn within safe range
        if (angle >= 0 and angle <= MAX_BASE_ANGLE):
            self.base_motor.run_target(BASE_MOTOR_SPEED, angle, then=Stop.HOLD)
# endregion

# region openGripper()
    def openGripper(self):
        self.gripper_motor.run_target(GRIPPER_MOTOR_SPEED, -90, then=Stop.COAST)
# endregion

# region closeGripper()
    def closeGripper(self):
        # Close the gripper untill motor stalls and holds it there
        # The goal is to return True if something is picked up else False
        self.gripper_motor.run_until_stalled(GRIPPER_MOTOR_SPEED, then=Stop.HOLD, duty_limit=45)

        if (self.gripper_motor.angle() < -5):
            return True
        else:
            return False    
# endregion

# region Move Elbow

    def elbowDown(self):
        self.elbow_motor.run_target(ELBOW_MOTOR_SPEED, GROUND_HIGHT, then=Stop.HOLD)

    def elbowUp(self):
        self.elbow_motor.run_target(ELBOW_MOTOR_SPEED, SENSOR_HIGHT, then=Stop.HOLD) 

# endregion 

# region dropBlock

    def dropBlock(self):
        self.elbowDown()
        self.openGripper()
        self.elbowUp()

# endregion

# region goToDropOff(index)
    def goToDropOff(self, index):
        self.turnBase(self.dropOffAngle[index])
# endregion

# region goToPickUp
    def goToPickUp(self):
        self.turnBase(self.pickUp)
# endregion

# region dropOffAt(index)
    def dropOffAt(self, index):
        self.goToDropOff(index)
        self.dropBlock()
# endregion

# region dropOffAtColor(color)
    def dropOffAtColor(self, color):
        if color in self.dropOffColor:
            self.goToDropOff(self.dropOffColor.index(color))
            color2 = self.elbow_sensor.color()
            if (color == color2):
                self.dropBlock()
            else:   
                return False
            return True
        else:
            return False

# endregion




# region defaultPickUpBlock()
    def defaultPickUpBlock(self):
        self.goToPickUp()

        self.openGripper()
        self.elbowDown()
        blockPresent = self.closeGripper()
        self.elbowUp()

        if blockPresent:
            color, size = self.getColor()
            blockPresent = self.drawColor(color)
            
        else:
            color = None
        
        wait(100)
        print("Last gripper: ", self.gripper_motor.angle())
        if (self.gripper_motor.angle() > -10 or color == None):
            blockPresent = False
        else:
            blockPresent = True    
        
        return blockPresent, color

# endregion

    def pickUpFromHight(self):

            self.elbow_motor.run_target(ELBOW_MOTOR_SPEED, ELEVATED_HEIGHT + 10, then=Stop.HOLD)
            self.goToPickUp()
            self.openGripper()
            self.elbow_motor.run_target(ELBOW_MOTOR_SPEED, ELEVATED_HEIGHT, then=Stop.HOLD)
            blockPresent = self.closeGripper()
            self.elbow_motor.run_target(ELBOW_MOTOR_SPEED, SENSOR_HIGHT - 3, then=Stop.HOLD) 

            if blockPresent:
                color, size = self.getColor()
                blockPresent = self.drawColor(color)
                
            else:
                color = None

            wait(100)
            print("Last gripper: ", self.gripper_motor.angle())
            if (self.gripper_motor.angle() > -10 or color == None):
                blockPresent = False
            else:
                blockPresent = True

            return blockPresent, color


    def getColor(self):
        size = "SMALL"
        color = self.elbow_sensor.color()
        brickSize = self.elbow_sensor.reflection()
        #print(color)
        if color == Color.RED:
            if brickSize > 50:
                size = "BIG"
        elif color == Color.GREEN or color == Color.BLUE or color == Color.BLACK:
            if brickSize > 9:
                size = "BIG"
            colorTest = self.elbow_sensor.rgb()
            print(colorTest)
            if colorTest[2] > colorTest[1]:
                color = Color.BLUE
            else:
                color = Color.GREEN
            
        elif color == Color.YELLOW or color == Color.BROWN:
            color = Color.YELLOW
            if brickSize < 50:
                size = "BIG"
        else:
            color = None
            size = "UNKNOWN"
        return color, size

    def getSizeColorAt(self,index):
        self.goToDropOff(index)
        self.openGripper()
        self.elbowDown()
        blockPresent = self.closeGripper()
        self.elbowUp()

        if blockPresent:
            color, size = self.getColor()
            blockPresent = self.drawColor(color)
            
        else:
            color = None
            size = "UNKNOWN"

        self.elbowDown()
        self.openGripper()
        self.elbowUp()
        self.goToPickUp()

        return color, size

def main():

    test = 1
    robot = Robot(SENSOR_HIGHT, BASESWITCH_OFFSET)
    dropoffzone = 0
    while True:
        
        if test == 1:
            blockPresent, color = robot.pickUpFromHight()
        else:
            blockPresent, color = robot.defaultPickUpBlock()
        wait(100)
        if (blockPresent):
            blockPresent = not robot.dropOffAtColor(color)
               

        if (blockPresent and robot.elbow_sensor.color() != None):
            wait(1000)
            robot.dropBlock()

        wait(3000)


if __name__== "__main__":
    main() 
