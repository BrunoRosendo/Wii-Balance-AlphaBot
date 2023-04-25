import RPi.GPIO as GPIO
from adafruit_servokit import ServoKit
from picamera import PiCamera

class Camera:
    def __init__(self):
        self.cam = PiCamera()
        self.kit = ServoKit(channels=16) # number of channels (hardware)
    
    """
    Changes the tilt angle (left to right), between 20 and 150
    """
    def tilt(self, angle):
        if angle > 150:
            self.kit.servo[0].angle = 150
        elif angle < 20:
            self.kit.servo[0].angle = 20
        else:
            self.kit.servo[0].angle = angle

    """
    Changes the pan angle (top to bottom), between 20 and 150
    """
    def pan(self, angle):
        if angle > 150:
            self.kit.servo[1].angle = 150
        elif angle < 20:
            self.kit.servo[1].angle = 20
        else:
            self.kit.servo[1].angle = angle

    """
    Resets the camera to the default position
    """
    def reset(self):
        print("resetting camera")
        self.tilt(0)
        self.pan(0)
    
    """
    Starts the camera preview
    """
    def preview(self):
        self.cam.preview()
