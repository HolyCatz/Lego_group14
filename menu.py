#!/usr/bin/env pybricks-micropython

from pybricks.hubs import EV3Brick
from pybricks.ev3devices import Motor, TouchSensor, ColorSensor
from pybricks.parameters import Port, Stop, Direction, Color, Button
from pybricks.tools import wait

MAX_BASE_ANGLE = 260        # NOTE: Set the angle to an apropriate value

BASE_MOTOR_SPEED = 60
GRIPPER_MOTOR_SPEED = 200
ELBOW_MOTOR_SPEED = 60

SENSOR_HIGHT = 64
GROUND_HIGHT = 30

BASESWITCH_OFFSET = 7

DROP_OFF1   = 100
DROP_OFF2   = 150
DROP_OFF3   = 200
PICKUP      = 0

DEBOUNCE_TIME = 300         # Wait time after a button press so it only get's registered once





class Robot:


# region Constructor

    def __init__(self):
        self.ev3 = EV3Brick()
        self.gripper_motor = Motor(Port.A)
        self.elbow_motor = Motor(Port.B, Direction.COUNTERCLOCKWISE, [8, 40])
        self.base_motor = Motor(Port.C, Direction.COUNTERCLOCKWISE, [12, 36])

        self.base_switch = TouchSensor(Port.S1)
        self.elbow_sensor = ColorSensor(Port.S2)
        self.elbow_motor.control.limits(speed=ELBOW_MOTOR_SPEED, acceleration=120)
        self.base_motor.control.limits(speed=BASE_MOTOR_SPEED, acceleration=120)
        self.dropOffColor = [Color.BLUE, Color.RED, Color.GREEN]



    def buttonTest(self):
            # Check if any button is pressed
        while True:
            # Check if any button is pressed
            pressed = self.ev3.buttons.pressed()

            # If the center button is pressed, break the loop
            if Button.CENTER in pressed:
                print("Center button pressed, exiting.")
                self.base_motor.hold()
                break

            # Check for other buttons and perform actions
            if Button.UP in pressed:
                print("Up button pressed")
                wait(100)
            elif Button.DOWN in pressed:
                print("Down button pressed")
                wait(100)
            elif Button.LEFT in pressed:
                print("Left button pressed")
                wait(100)
            elif Button.RIGHT in pressed:
                print("Right button pressed")
                wait(100)
            
            # Small delay to prevent button bounce
            wait(100)

    def menuDraw(self):
        self.main_menu = ["Start", "Set Drop Off", "test2", "Stop"]
        self.set_dropoff = ["Zone 1: ", "Zone 2: ", "Zone 3: "]
        self.set_color = ["Red", "Green", "Blue", "Yellow"]

        menu_title = ["Main Menu", "Set Dropoff Color"]


        color_names = {
            Color.BLUE: "Blue",
            Color.RED: "Red",
            Color.GREEN: "Green",
            Color.YELLOW: "Yellow"
        }



        self.menu_items = [self.main_menu, self.set_dropoff, self.set_color]

        self.ev3.screen.clear()

        if self.menu_title_txt == "":
            self.ev3.screen.draw_text(0,0, menu_title[self.menu_selection])
        else:
            self.ev3.screen.draw_text(0,0, self.menu_title_txt)


        for index, item in enumerate(self.menu_items[self.menu_selection]):
            if (self.menu_selection == 1):
                item += color_names[self.dropOffColor[index]]

            if index == self.item_selection:
                # Highlight the selected item by inverting the colors
                self.ev3.screen.draw_text(0, index * 20 + 30, item, text_color=Color.WHITE, background_color=Color.BLACK)
            else:
                self.ev3.screen.draw_text(0, index * 20 + 30, item)
                



    def menuLoop(self):
        self.menu_selection = 0
        self.item_selection = 0
        self.menu_title_txt = ""


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
                self.item_selection = (self.item_selection + 1) % len(self.menu_items[self.menu_selection])
                wait(DEBOUNCE_TIME)
            elif Button.UP in pressed:
                self.item_selection = (self.item_selection - 1) % len(self.menu_items[self.menu_selection])
                wait(DEBOUNCE_TIME)

        
            elif Button.CENTER in pressed:
                if self.menu_selection == 0:
                    # Main menu
                    if self.item_selection == 1:
                        self.menu_selection = 1
                        self.item_selection = 0
                    elif self.item_selection == len(self.main_menu) - 1:
                        break 
                elif self.menu_selection == 1:
                    # Set dropoff color
                    selected_zone = self.item_selection
                    self.menu_title_txt = "Set Color For: Zone " + str(self.item_selection)
                    self.menu_selection = 2
                    self.item_selection = 0
                elif self.menu_selection == 2:
                    # Choose color for zone
                    self.dropOffColor[selected_zone] = color_index[self.item_selection]
                    self.menu_selection = 1
                    self.menu_title_txt = ""
                    self.item_selection = selected_zone
                
                
                
                
                wait(DEBOUNCE_TIME)



        
            elif Button.LEFT in pressed:
                if self.menu_selection == 1:
                    self.menu_selection = 0
                    self.menu_title_txt = ""
                if self.menu_selection == 2:
                    self.menu_selection = 1
                    self.menu_title_txt = ""

                self.item_selection = 0
                wait(DEBOUNCE_TIME)
            else:
                wait(100)



def main():

    robot = Robot()


    print("menu")

    robot.menuLoop()

    print("Done!")

    
    # robot.base_motor.run_target(BASE_MOTOR_SPEED, 160, then=Stop.COAST, wait=False)
    # robot.buttonTest()

    



if __name__== "__main__":
    main() 