from Alphabot import Alphabot
import RPi.GPIO as GPIO

alphabot = Alphabot()
alphabot.stop()
GPIO.cleanup()
