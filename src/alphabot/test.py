from Alphabot import Alphabot

alphabot = Alphabot()
forward = False

def toggle_forward_backwards():
    if forward:
        alphabot.drive_backwards()
        forward = False
    else:
        alphabot.drive_forward()
        forward = True
