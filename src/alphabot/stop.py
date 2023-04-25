from Alphabot import Alphabot
from Camera import Camera
import RPi.GPIO as GPIO

alphabot = Alphabot()
alphabot.stop()

cam = Camera()
cam.stop()

GPIO.cleanup()
