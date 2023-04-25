from alphabot.Alphabot import Alphabot
from alphabot.Camera import Camera

alphabot = Alphabot()
cam = Camera()
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
