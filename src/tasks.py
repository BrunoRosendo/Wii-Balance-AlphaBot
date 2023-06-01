from alphabot.Alphabot import Alphabot
from alphabot.Camera import Camera
from wii_balance.WiiBoard import ResponseType, WiiBoard
import time

alphabot = Alphabot()
cam = Camera()
wiiBoard = WiiBoard()   # Initialize the board. TODO: Check if should be here

forward = False

def toggle_forward_backwards():
    global forward
    if forward:
        alphabot.drive_backwards()
        forward = False
    else:
        alphabot.drive_forward()
        forward = True

action = 0
def all_actions():
    global action
    if action == 0:
        alphabot.drive_forward()
    elif action == 1:
        alphabot.drive_backwards()
    elif action == 2:
        alphabot.drive_left()
    elif action == 3:
        alphabot.drive_right()
    elif action == 4:
        alphabot.stop()
    action = (action + 1) % 5

def init_camera():
    cam.reset()
    cam.preview()

def read_wii_data():
    print("Reading wii data......")
    # Read the balance board data
    response = wiiBoard.read_data()
    if (response != None):
        respType = response["type"]
        data = response["data"]
        print("Response type:", respType)
        if respType == ResponseType.STATUS:
            print(f"{respType} - {data}")
        elif respType == ResponseType.CALIBRATION:
            print(f"{respType} - {data}")
        elif respType == ResponseType.MASS:
            print(f"{respType} - {data}")
            alphabot.mass_to_velocity(data)
            print(alphabot.vertDirection, alphabot.horizDirection, 
                  alphabot.vertPower, alphabot.horizPower)
        elif respType == ResponseType.BUTTON:
            print(f"{respType} - {data}")
            alphabot.setHonk(data)
            print("Here")
    else:
        print("No Response")

def drive_alphabot():
    print("Driving alpha bot.....")
    # time.sleep(1)
    # print("Out of sleep")
    alphabot.drive()

def connect_to_board():
    print("Connecting to board...\n\n")
    wiiBoard.connectToBoard()
    
def honk():
    print("HONK HONK")
    alphabot.updateBuzzer()
# TODO: Detect when the board is disconnected
