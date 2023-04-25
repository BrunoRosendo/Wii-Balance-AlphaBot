import RPi.GPIO as GPIO
from adafruit_servokit import ServoKit
from picamera import PiCamera

class Camera:
    def __init__(self):
        self.cam = PiCamera()
        self.kit = ServoKit(channels=16) # number of channels (hardware)
    
    """
    Changes the tilt angle (left to right), between 0 and 150
    """
    def tilt(self, angle):
        if angle > 150:
            self.kit.servo[0].angle = 150
        elif angle < 0:
            self.kit.servo[0].angle = 0
        else:
            self.kit.servo[0].angle = angle

    """
    Changes the pan angle (top to bottom), between 0 and 150
    """
    def pan(self, angle):
        if angle > 150:
            self.kit.servo[1].angle = 150
        elif angle < 0:
            self.kit.servo[1].angle = 0
        else:
            self.kit.servo[1].angle = angle

    """
    Resets the camera to the default position
    """
    def reset(self):
        self.tilt(0)
        self.pan(30)

    """
    Starts the camera preview
    """
    def preview(self):
        self.cam.start_preview()
    
    """
    Stops the camera preview and servo
    """
    def stop(self):
        self.cam.stop_preview()
        self.kit.servo[0].angle = None
        self.kit.servo[1].angle = None
