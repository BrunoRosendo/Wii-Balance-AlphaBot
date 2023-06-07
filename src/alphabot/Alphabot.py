import RPi.GPIO as GPIO
from enum import Enum

class MovDirection(Enum):
    POSITIVE = 0
    NEGATIVE = 1
    IDLE = 2

# Weights that define the motor velocity
weightThreshold = {
    "NONE": 5,
    "LOW": 10,
    "MEDIUM": 15,
    "HIGH": 20,
    "VERY_HIGH": 30
}
# Power that defines the motor velocity
powerMap = {
    "NONE": 0,
    "LOW": 10,
    "MEDIUM": 20,
    "HIGH": 30,
    "VERY_HIGH": 40
}
powerIncrement = powerMap["MEDIUM"] - powerMap["LOW"]

class Alphabot:
    def __init__(self, ain1=12, ain2=13, bin1=20, bin2=21, ena=6, enb=26, vertPower=50, horizPower=30, irLeft = 16, irRight = 19):
        self.ain1 = ain1 # motor A right forwards
        self.ain2 = ain2 # motor A backwards
        self.bin1 = bin1 # motor B forwards
        self.bin2 = bin2 # motor B backwards
        self.ena = ena # enable pin for motor A
        self.enb = enb # enable pin for motor B

        # Variables to control the speed of the motors
        self.vertPower = vertPower # duty cycle of the PWM signal of the motors (0-100 percentage)
        self.horizPower = horizPower # duty cycle of the PWM signal of the motors  (0-100 percentage)

        # Variables to control the direction of the motors
        self.vertDirection = MovDirection.IDLE # vertical velocity of the robot
        self.horizDirection = MovDirection.IDLE # horizontal velocity of the robot

        # Variable to check if the alpha is close to colliding
        self.isColliding = False

        # Variable to control if the buzzer should be on or off
        self.honk = False
        self.buzzer = 4	# BUZZER PIN
        

        # Variables to control the IR sensors
        self.irLeft = irLeft
        self.irRight = irRight

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.buzzer, GPIO.OUT)
        GPIO.setup(self.ain1, GPIO.OUT)
        GPIO.setup(self.ain2, GPIO.OUT)
        GPIO.setup(self.bin1, GPIO.OUT)
        GPIO.setup(self.bin2, GPIO.OUT)
        GPIO.setup(self.ena, GPIO.OUT)
        GPIO.setup(self.enb, GPIO.OUT)
        GPIO.setup(self.irLeft, GPIO.IN)
        GPIO.setup(self.irRight, GPIO.IN)
        self.pwma = GPIO.PWM(self.ena, 500)
        self.pwmb = GPIO.PWM(self.enb, 500)
        self.pwma.start(self.vertPower)
        self.pwmb.start(self.vertPower)

        self.stop()

    """
    Drives forward, using both wheels
    """
    def drive_forward(self):
        self.pwma.ChangeDutyCycle(self.vertPower)
        self.pwmb.ChangeDutyCycle(self.vertPower)
        GPIO.output(self.ain1, GPIO.LOW)
        GPIO.output(self.ain2, GPIO.HIGH)
        GPIO.output(self.bin1, GPIO.LOW)
        GPIO.output(self.bin2, GPIO.HIGH)

    """
    Drives backwards, using both wheels
    """
    def drive_backwards(self):
        self.pwma.ChangeDutyCycle(self.vertPower)
        self.pwmb.ChangeDutyCycle(self.vertPower)
        GPIO.output(self.ain1, GPIO.HIGH)
        GPIO.output(self.ain2, GPIO.LOW)
        GPIO.output(self.bin1, GPIO.HIGH)
        GPIO.output(self.bin2, GPIO.LOW)

    """
    Drives while turning to the left
    """
    def drive_left(self):
        self.pwma.ChangeDutyCycle(self.horizPower)
        self.pwmb.ChangeDutyCycle(self.horizPower)
        GPIO.output(self.ain1, GPIO.HIGH)
        GPIO.output(self.ain2, GPIO.LOW)
        GPIO.output(self.bin1, GPIO.LOW)
        GPIO.output(self.bin2, GPIO.HIGH)

    """
    Drives while turning to the right
    """
    def drive_right(self):
        self.pwma.ChangeDutyCycle(self.horizPower)
        self.pwmb.ChangeDutyCycle(self.horizPower)
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
        horizDirection = MovDirection.POSITIVE if right >= left else MovDirection.NEGATIVE if left > right else MovDirection.IDLE

        print(f"vertDiff {vertDiff} horizDiff {horizDiff}")
        # Decide the vertical movement
        if vertDiff <= weightThreshold["NONE"]: # No movement
            self.vertDirection = MovDirection.IDLE
            self.vertPower = 0
        elif vertDiff <= weightThreshold["LOW"]: # Low movement
            self.vertDirection = vertDirection
            self.vertPower = powerMap["LOW"]
        elif vertDiff <= weightThreshold["MEDIUM"]: # Medium movement
            self.vertDirection = vertDirection
            self.vertPower = powerMap["MEDIUM"]
        elif vertDiff <= weightThreshold["HIGH"]: # High movement
            self.vertDirection = vertDirection
            self.vertPower = powerMap["HIGH"]
        elif vertDiff <= weightThreshold["VERY_HIGH"]: # Very High movement
            self.vertDirection = vertDirection
            self.vertPower = powerMap["VERY_HIGH"]

        # Decide the horizontal movement
        if horizDiff <= weightThreshold["NONE"]: # No movement
            self.horizDirection = MovDirection.IDLE
            self.horizPower = 0
        elif horizDiff <= weightThreshold["LOW"]: # Low movement
            self.horizDirection = horizDirection
            self.horizPower = powerMap["LOW"]
        elif horizDiff <= weightThreshold["MEDIUM"]: # Medium movement
            self.horizDirection = horizDirection
            self.horizPower = powerMap["MEDIUM"]
        elif horizDiff <= weightThreshold["HIGH"]: # High movement
            self.horizDirection = horizDirection
            self.horizPower = powerMap["HIGH"]
        elif horizDiff <= weightThreshold["VERY_HIGH"]: # Very High movement
            self.horizDirection = horizDirection
            self.horizPower = powerMap["VERY_HIGH"]

    """
    Decides the direction of the robot and drives accordingly
    """
    def drive(self):
        # print("Entered drive...")
        rightMotorPower = 0
        leftMotorPower = 0            
        isRotating = False  # True if the robot is rotating. Will be updated inside
        
        if (self.vertDirection == MovDirection.IDLE and self.horizDirection == MovDirection.IDLE) or (self.vertDirection == MovDirection.POSITIVE and self.isColliding):
            # Stop
            self.stop()
            return
        elif (self.vertDirection != MovDirection.IDLE):
            rightMotorPower = self.vertPower
            leftMotorPower = self.vertPower
            if (self.horizDirection == MovDirection.POSITIVE):
                # Drive forward and right
                # Change the power of the wheels to turn (leftPower > rightPower)
                leftMotorPower = max(self.vertPower, self.horizPower)
                rightMotorPower = min(self.vertPower, self.horizPower)
                if leftMotorPower == rightMotorPower:   # If the powers are equal, force the left motor to be stronger
                    rightMotorPower -= powerIncrement   # Decrease the power of the right motor
            elif (self.horizDirection == MovDirection.NEGATIVE):
                # Drive forward and left
                # Change the power of the wheels to turn (rightPower > leftPower)
                rightMotorPower = max(self.vertPower, self.horizPower)
                leftMotorPower = min(self.vertPower, self.horizPower)
                if leftMotorPower == rightMotorPower:   # If the powers are equal, force the right motor to be stronger
                    leftMotorPower -= powerIncrement   # Decrease the power of the left motor
            #else:
                # Drive forward
                # The motors power is already set
        elif (self.horizDirection != MovDirection.IDLE):
            rightMotorPower = self.horizPower
            leftMotorPower = self.horizPower
            isRotating = True   # The robot is rotating (special case)
            # The other cases were already set
        else:
           print("Error: Unknown direction")
           return
        
        attenuator = 2 if isRotating else 1 # Attenuate the power of the motors if we are rotating
        
        # Set the power of the motors
        self.pwma.ChangeDutyCycle(leftMotorPower / attenuator)
        self.pwmb.ChangeDutyCycle(rightMotorPower / attenuator)

        # Set the direction of the motors
        # The vertical direction determines if we turn on the motor1 or motors2
        if self.vertDirection == MovDirection.POSITIVE:
            GPIO.output(self.ain1, GPIO.LOW)
            GPIO.output(self.ain2, GPIO.HIGH)
            GPIO.output(self.bin1, GPIO.LOW)
            GPIO.output(self.bin2, GPIO.HIGH)
        elif self.vertDirection == MovDirection.NEGATIVE:
            GPIO.output(self.ain1, GPIO.HIGH)
            GPIO.output(self.ain2, GPIO.LOW)
            GPIO.output(self.bin1, GPIO.HIGH)
            GPIO.output(self.bin2, GPIO.LOW)
        else: # Horizontal Movement (special case)
            if self.horizDirection == MovDirection.POSITIVE:
                # Turn left
                GPIO.output(self.ain1, GPIO.LOW)
                GPIO.output(self.ain2, GPIO.HIGH)
                GPIO.output(self.bin1, GPIO.HIGH)
                GPIO.output(self.bin2, GPIO.LOW)
            elif self.horizDirection == MovDirection.NEGATIVE:
                # Turn right
                GPIO.output(self.ain1, GPIO.HIGH)
                GPIO.output(self.ain2, GPIO.LOW)
                GPIO.output(self.bin1, GPIO.LOW)
                GPIO.output(self.bin2, GPIO.HIGH)
                
    def setHonk(self, value):
        """
        Sets the value of the honk to True or False
        """
        self.honk = value
        
    def updateBuzzer(self):
        """
        Updates the Buzzer according to the current value of the honk
        """
        val = GPIO.LOW
        if self.honk == True:
            val = GPIO.HIGH
        
        GPIO.output(self.buzzer, val)


    """
    Checks if the robot will collide with something
    """
    def checkCollision(self):
        # print("left sensor", GPIO.input(self.irLeft))
        # print("right sensor", GPIO.input(self.irRight))
        self.isColliding = not GPIO.input(self.irLeft) or not GPIO.input(self.irRight)

        



