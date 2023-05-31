import RPi.GPIO as GPIO
from enum import Enum

class MovDirection(Enum):
    POSITIVE = 0
    NEGATIVE = 1
    IDLE = 2

# Weights that define the motor velocity
weightThreshold = {
    "NONE": 10,
    "LOW": 20,
    "MEDIUM": 30,
    "HIGH": 40
}
# Power that defines the motor velocity
powerMap = {
    "NONE": 0,
    "LOW": 25,
    "MEDIUM": 50,
    "HIGH": 75
}

class Alphabot:
    def __init__(self, ain1=12, ain2=13, bin1=20, bin2=21, ena=6, enb=26, drivingPower=50, turningPower=30):
        self.ain1 = ain1 # motor A right forwards
        self.ain2 = ain2 # motor A backwards
        self.bin1 = bin1 # motor B forwards
        self.bin2 = bin2 # motor B backwards
        self.ena = ena # enable pin for motor A
        self.enb = enb # enable pin for motor B

        # Variables to control the speed of the motors
        self.drivingPower = drivingPower # duty cycle of the PWM signal of the motors (0-100 percentage)
        self.turningPower = turningPower # duty cycle of the PWM signal of the motors  (0-100 percentage)

        # Variables to control the direction of the motors
        self.vertDirection = MovDirection.IDLE # vertical velocity of the robot
        self.horizDirection = MovDirection.IDLE # horizontal velocity of the robot

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.ain1, GPIO.OUT)
        GPIO.setup(self.ain2, GPIO.OUT)
        GPIO.setup(self.bin1, GPIO.OUT)
        GPIO.setup(self.bin2, GPIO.OUT)
        GPIO.setup(self.ena, GPIO.OUT)
        GPIO.setup(self.enb, GPIO.OUT)
        self.pwma = GPIO.PWM(self.ena, 500)
        self.pwmb = GPIO.PWM(self.enb, 500)
        self.pwma.start(self.drivingPower)
        self.pwmb.start(self.drivingPower)

        self.stop()

    """
    Drives forward, using both wheels
    """
    def drive_forward(self):
        self.pwma.ChangeDutyCycle(self.drivingPower)
        self.pwmb.ChangeDutyCycle(self.drivingPower)
        GPIO.output(self.ain1, GPIO.LOW)
        GPIO.output(self.ain2, GPIO.HIGH)
        GPIO.output(self.bin1, GPIO.LOW)
        GPIO.output(self.bin2, GPIO.HIGH)

    """
    Drives backwards, using both wheels
    """
    def drive_backwards(self):
        self.pwma.ChangeDutyCycle(self.drivingPower)
        self.pwmb.ChangeDutyCycle(self.drivingPower)
        GPIO.output(self.ain1, GPIO.HIGH)
        GPIO.output(self.ain2, GPIO.LOW)
        GPIO.output(self.bin1, GPIO.HIGH)
        GPIO.output(self.bin2, GPIO.LOW)

    """
    Drives while turning to the left
    """
    def drive_left(self):
        self.pwma.ChangeDutyCycle(self.turningPower)
        self.pwmb.ChangeDutyCycle(self.turningPower)
        GPIO.output(self.ain1, GPIO.HIGH)
        GPIO.output(self.ain2, GPIO.LOW)
        GPIO.output(self.bin1, GPIO.LOW)
        GPIO.output(self.bin2, GPIO.HIGH)

    """
    Drives while turning to the right
    """
    def drive_right(self):
        self.pwma.ChangeDutyCycle(self.turningPower)
        self.pwmb.ChangeDutyCycle(self.turningPower)
        GPIO.output(self.ain1, GPIO.LOW)
        GPIO.output(self.ain2, GPIO.HIGH)
        GPIO.output(self.bin1, GPIO.HIGH)
        GPIO.output(self.bin2, GPIO.LOW)

    """
    Stops both wheels and the pwm signal
    """
    def stop(self):
        self.pwma.ChangeDutyCycle(0)
        self.pwmb.ChangeDutyCycle(0)
        GPIO.output(self.ain1, GPIO.LOW)
        GPIO.output(self.ain2, GPIO.LOW)
        GPIO.output(self.bin1, GPIO.LOW)
        GPIO.output(self.bin2, GPIO.LOW)

    """
    Convert the mass data from the WiiBoard to a velocity
    Update the direction and power of the motors of the Alphabot accordingly
    Parameters
    ----------
    mass: {'top_right': float, 'top_left': float, 'bottom_right': float, 'bottom_left': float}
    """
    def mass_to_velocity(self, mass):
        up = (mass["top_right"] + mass["top_left"]) / 2
        down = (mass["bottom_right"] + mass["bottom_left"]) / 2
        left = (mass["top_left"] + mass["bottom_left"]) / 2
        right = (mass["top_right"] + mass["bottom_right"]) / 2

        # Calculate the difference between the masses and directions
        vertDiff = abs(up - down)
        vertDirection = MovDirection.POSITIVE if up >= down else MovDirection.NEGATIVE if down > up else MovDirection.IDLE
        horizDiff = abs(left - right)
        horizDirection = MovDirection.POSITIVE if left >= right else MovDirection.NEGATIVE if right > left else MovDirection.IDLE

        # Set the direction and power of the motors
        # Decide if movement is vertical or horizontal
        if vertDiff >= horizDiff:
            # Reset the horizontal movement
            self.horizDirection = MovDirection.IDLE
            self.turningPower = 0
            # Decide the vertical movement
            if vertDiff <= weightThreshold["NONE"]: # No movement
                self.vertDirection = MovDirection.IDLE
                self.drivingPower = 0
            elif vertDiff <= weightThreshold["LOW"]: # Low movement
                self.vertDirection = vertDirection
                self.drivingPower = powerMap["LOW"]
            elif vertDiff <= weightThreshold["MEDIUM"]: # Medium movement
                self.vertDirection = vertDirection
                self.drivingPower = powerMap["MEDIUM"]
            elif vertDiff <= weightThreshold["HIGH"]: # High movement
                self.vertDirection = vertDirection
                self.drivingPower = powerMap["HIGH"]
        else:
            # Reset the vertical movement
            self.vertDirection = MovDirection.IDLE
            self.drivingPower = 0
            # Decide the horizontal movement
            if horizDiff <= weightThreshold["NONE"]:
                self.horizDirection = MovDirection.IDLE
                self.turningPower = 0
            elif horizDiff <= weightThreshold["LOW"]:
                self.horizDirection = horizDirection
                self.turningPower = powerMap["LOW"]
            elif horizDiff <= weightThreshold["MEDIUM"]:
                self.horizDirection = horizDirection
                self.turningPower = powerMap["MEDIUM"]
            elif horizDiff <= weightThreshold["HIGH"]:
                self.horizDirection = horizDirection
                self.turningPower = powerMap["HIGH"]

    """
    Decides the direction of the robot and drives accordingly
    """
    def drive(self):
        if (self.vertDirection == MovDirection.IDLE and self.horizDirection == MovDirection.IDLE):
            # Stop
            self.stop()
        elif (self.vertDirection == MovDirection.POSITIVE):
            # Drive forward
            self.drive_forward()
        elif (self.vertDirection == MovDirection.NEGATIVE):
            # Drive backwards
            self.drive_backwards()
        elif (self.horizDirection == MovDirection.POSITIVE):
            # Drive right
            self.drive_right()
        elif (self.horizDirection == MovDirection.NEGATIVE):
            # Drive left
            self.drive_left()
        else:
           print("Error: Unknown direction")
        

        



