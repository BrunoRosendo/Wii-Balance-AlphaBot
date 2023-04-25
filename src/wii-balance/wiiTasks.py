#! /usr/bin/env python
""" Wii Fit Balance Board (WBB) in python

usage: wiiboard.py [-d] [address] 2> wiiboard.log > wiiboard.txt
tip: use `hcitool scan` to get a list of devices addresses

You only need to install `python-bluez` or `python-bluetooth` package.

LICENSE LGPL <http://www.gnu.org/licenses/lgpl.html>
        (c) Nedim Jackman 2008 (c) Pierrick Koch 2016
"""
import time
import logging
import collections
import bluetooth
import socket
import struct
from enum import Enum

# Wiiboard Parameters
CONTINUOUS_REPORTING    = b'\x04'
COMMAND_LIGHT           = b'\x11'
COMMAND_REPORTING       = b'\x12'
COMMAND_REQUEST_STATUS  = b'\x15'
COMMAND_REGISTER        = b'\x16'
COMMAND_READ_REGISTER   = b'\x17'   # TODO: Check if should change to hex
INPUT_STATUS            = 0x20
INPUT_READ_DATA         = 0x21
EXTENSION_8BYTES        = 0x32
BUTTON_DOWN_MASK        = 0x08
LED1_MASK               = 0x10
BATTERY_MAX             = 200.0
TOP_RIGHT               = 0
BOTTOM_RIGHT            = 1
TOP_LEFT                = 2
BOTTOM_LEFT             = 3
BLUETOOTH_NAME          = "Nintendo RVL-WBC-01"
# WiiboardSampling Parameters
N_SAMPLES               = 200
N_LOOP                  = 10
T_SLEEP                 = 2
# Socket Parameters
SEND_SOCKET_PORT        = 0x11
RECV_SOCKET_PORT        = 0x13
# Wiiboard payloads
CALIBRATION_REQ_PAYLOAD = b"\x04\xA4\x00\x24\x00\x18"
MASS_REQ_PAYLOAD        = b"\x04\xA4\x00\x40\x00"

# initialize the logger
logger = logging.getLogger(__name__)
handler = logging.StreamHandler() # or RotatingFileHandler
handler.setFormatter(logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s] %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO) # or DEBUG

class ResponseType(Enum):
    STATUS = 0
    CALIBRATION = 1
    MASS = 2
    BUTTON = 3

class WiiBoard():
    def __init__(self):
        self.discover()
        self.connect()
        self.calibrate()
        self.readCalibrationData()

    def discover(self, duration=6, prefix=BLUETOOTH_NAME):
        '''
        Discover the WiiBoard (1)

        Parameters:
        -------------
        duration : int 
            The duration of the discovery in seconds
        prefix : str
            The prefix of the WiiBoard name
        '''
        logger.info("Scan Bluetooth devices for %i seconds...", duration)
        devices = bluetooth.discover_devices(duration=duration, lookup_names=True)
        logger.debug("Found devices: %s", str(devices))
        found_boards = [address for address, name in devices if name.startswith(prefix)]
        if not found_boards or len(found_boards) == 0:
            raise Exception("[Discovery] No WiiBoard found")
        
        self.board_address = found_boards[0]
        logger.info("Found WiiBoard: %s" % self.board_address)

    def connect(self):
        '''
        Connect to the WiiBoard (2)
        ''' 
        self.controlSocket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_L2CAP)
        self.receiveSocket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_L2CAP)
        self.calibration = [[1e4]*4]*3
        self.calibration_requested = False
        self.calibrated = False
        self.light_state = False
        self.button_down = False
        self.battery = 0.0
        self.running = True
        if self.board_address is None:
            raise Exception("[Connect] No WiiBoard address found")

        logger.info("Connecting to %s", self.board_address)
        self.controlSocket.connect((self.board_address, SEND_SOCKET_PORT))
        self.receiveSocket.connect((self.board_address, RECV_SOCKET_PORT))
        logger.info("Connected sockets")

    def calibrate(self):
        '''
        Calibrate the WiiBoard (3)
        '''
        logger.debug("Sending mass calibration request")
        self.send(COMMAND_READ_REGISTER, CALIBRATION_REQ_PAYLOAD)
        self.calibration_requested = True
        logger.info("Wait for calibration")

        logger.debug("Connect to the balance extension, to read mass data")
        self.send(COMMAND_REGISTER, MASS_REQ_PAYLOAD)
        logger.debug("Request status")

        self.status()
        self.light(False)

    def readCalibrationData(self):
        '''
        Read calibration data from the WiiBoard (4)
        '''
        logger.debug("Attempting to read calibration data...")
        while self.running and self.receiveSocket:
            data = self.receiveSocket.recv(25)
            # logger.debug("socket.recv(25): %r", data)
            if len(data) < 2:
                continue
            
            """ 
            hexCodes = [int(data.hex()[i:i+2], 16) for i in range(0, len(data.hex()), 2)]
            logger.debug("hexCodes", hexCodes)
            """

            # byteCodes = [int(data[i]) for i in range(0, len(data))]
            # logger.debug(f"byteCodes {byteCodes} {len(data)}")

            input_type = data[1] 
            logger.debug(f"input_type {input_type}")
            if input_type == INPUT_STATUS:
                # Handler for Status Messages
                batteryLevel = data[7]  # Get byte 7 from the packet
                logger.debug(f"[INPUT_TYPE] batteryLevel {batteryLevel}")
                self.battery = batteryLevel / BATTERY_MAX
                # 0x12: on, 0x02: off/blink
                # logger.debug("[INPUT_TYPE] data[4]", data[4])
                self.light_state = data[4] & LED1_MASK == LED1_MASK
                self.on_status()
            elif input_type == INPUT_READ_DATA:
                # Handler for calibration data
                logger.debug("Got calibration data")
                if self.calibration_requested:
                    # logger.debug(f"[INPUT_READ_DATA] data[4] {data[4]}")
                    length = int(data[4] / 16 + 1)
                    # logger.debug(f"[INPUT_READ_DATA] length: {length}")
                    data = data[7:7 + length]
                    cal = lambda d: [d[j:j+2] for j in [0, 2, 4, 6]]
                    if length == 16: # First packet of calibration data
                        self.calibration = [cal(data[0:8]), cal(data[8:16]), [1e4]*4]
                        continue
                    elif length < 16: # Second packet of calibration data
                        self.calibration[2] = cal(data[0:8])
                        self.calibration_requested = False
                        return self.on_calibrated()

    def read_data(self):
        '''
        Read data from the WiiBoard (5)
        '''
        logger.debug("Attempting to read data...")
        while self.running and self.receiveSocket:
            data = self.receiveSocket.recv(25)
            # logger.debug("socket.recv(25): %r", data)
            if len(data) < 2:   # Skip empty data
                continue
            
            """ 
            hexCodes = [int(data.hex()[i:i+2], 16) for i in range(0, len(data.hex()), 2)]
            logger.debug("hexCodes", hexCodes)
            """

            # byteCodes = [int(data[i]) for i in range(0, len(data))]
            # logger.debug(f"byteCodes {byteCodes} {len(data)}")

            input_type = data[1] 
            logger.debug(f"input_type {str(input_type)}")
            if input_type == INPUT_STATUS:
                # Handler for Status Messages
                batteryLevel = data[7]  # Get byte 7 from the packet
                logger.debug(f"[INPUT_TYPE] batteryLevel {batteryLevel}")
                self.battery = batteryLevel / BATTERY_MAX
                # 0x12: on, 0x02: off/blink
                # logger.debug("[INPUT_TYPE] data[4]", data[4])
                self.light_state = data[4] & LED1_MASK == LED1_MASK
                return self.on_status()
            elif input_type == INPUT_READ_DATA:
                # Handler for calibration data
                logger.debug("Got calibration data")
                if self.calibration_requested:
                    # logger.debug(f"[INPUT_READ_DATA] data[4] {data[4]}")
                    length = int(data[4] / 16 + 1)
                    # logger.debug(f"[INPUT_READ_DATA] length: {length}")
                    data = data[7:7 + length]
                    cal = lambda d: [d[j:j+2] for j in [0, 2, 4, 6]]
                    if length == 16: # First packet of calibration data
                        self.calibration = [cal(data[0:8]), cal(data[8:16]), [1e4]*4]
                        continue
                    elif length < 16: # Second packet of calibration data
                        self.calibration[2] = cal(data[0:8])
                        self.calibration_requested = False
                        return self.on_calibrated()
            elif input_type == EXTENSION_8BYTES:
                # Handler for Button and Mass data
                logger.debug("[EXTENSION] EXTENSION_8BYTES")
                if (not self.calibrated):   # If not calibrated, ignore
                    logger.info("Not calibrated, ignoring data")
                    continue

                buttonRes = self.check_button(data[2:4])
                if buttonRes is not None:   # If there is a button event
                    return buttonRes

                massVal = self.get_mass(data[4:12])
                return self.on_mass(massVal)

    def check_button(self, state):
        state_parsed = [state[i] for i in range(len(state))]
        logger.debug(f"Button state parsed: {state_parsed}")
        # Only the second byte of the state is the button state
        btn_state = state_parsed[1]
        if btn_state == BUTTON_DOWN_MASK:
            if not self.button_down:
                self.button_down = True
                return self.on_pressed()
        elif self.button_down:
            self.button_down = False
            return self.on_released()
        return None
        

    def get_mass(self, data):
        # logger.debug(f"[Get_Mass] data: {data}")
        # mass_data = [data[i] for i in range(len(data))]
        # logger.debug(f"[Get_Mass] mass_data: {mass_data}")
        return  {
            'top_right':    self.calc_mass(data[0:2], TOP_RIGHT),
            'bottom_right': self.calc_mass(data[2:4], BOTTOM_RIGHT),
            'top_left':     self.calc_mass(data[4:6], TOP_LEFT),
            'bottom_left':  self.calc_mass(data[6:8], BOTTOM_LEFT),
        }

    # Auxiliary functions
    def calc_mass(self, raw, pos):
        '''
        Calculate the mass read by the sensor

        Parameters:
            raw: bytes[2]
                raw data read by the sensor
            pos: int in [0, 3]
                Sensor Position (TOP_RIGHT, BOTTOM_RIGHT, TOP_LEFT, BOTTOM_LEFT)

        Returns:
            mass: mass read by the sensor
        '''
        # logger.debug(f"[Calc_Mass]raw: {raw} rawType {type(raw)}")

        # convert raw data (bytes) to int
        parsed_mass_aux = raw[0:2]
        # logger.debug(f"parsed_mass_aux {parsed_mass_aux}")

        parsed_mass = int.from_bytes(parsed_mass_aux, byteorder='big')
        # logger.debug(f"[Calc_Mass] parsed_mass: {parsed_mass}")

        # Check the hexadecimal value of raw data (2 int format)
        # parsed_mass_split = [parsed_mass_aux[i] for i in range(len(parsed_mass_aux))]
        # logger.debug(f"[Calc_Mass] parsed_mass_split: {parsed_mass_split}")
        
        # Convert Calibration data to int and extract the data from a specific pos
        calibration = [ int.from_bytes( [self.calibration[i][pos][j] for j in range(len(self.calibration[i][pos])) ], byteorder="big") for i in range(len(self.calibration)) ]
        # logger.debug(f"[Calc_Mass] Calibration: {calibration}")
        
        # Calculates the Kilogram weight reading from raw data at position pos
        # calibration[0] is calibration values for 0kg
        # calibration[1] is calibration values for 17kg
        # calibration[2] is calibratioposition of the sensorn values for 34kg
        if parsed_mass < calibration[0]:
            return 0.0
        elif parsed_mass < calibration[1]:
            return 17 * ((parsed_mass - calibration[0]) /
                         float((calibration[1] -
                                calibration[0])))
        else: # if parsed_mass >= calibration[1]:
            return 17 + 17 * ((parsed_mass - calibration[1]) /
                              float((calibration[2] -
                                     calibration[1])))


    def on_status(self):
        self.reporting() # Must set the reporting type after every status report
        logger.info("Status: battery: %.2f%% light: %s", self.battery*100.0, 'on' if self.light_state else 'off')
        self.light(1)

        status_data = {
            'battery': self.battery * 100.0,
            'light': self.light_state
        }
        return self.build_response(ResponseType.STATUS, status_data)

    def on_calibrated(self):
        logger.info("Board calibrated: %s", str(self.calibration))
        self.light(1)
        self.calibrated = True
        return self.build_response(ResponseType.CALIBRATION, self.calibration)
    def on_mass(self, mass):
        logger.debug("New mass data: %s", str(mass))
        return self.build_response(ResponseType.MASS, mass)
    def on_pressed(self):
        logger.info("Button pressed")
        return self.build_response(ResponseType.BUTTON, True)
    def on_released(self):
        logger.info("Button released")
        return self.build_response(ResponseType.BUTTON, False)
    def close(self):
        self.running = False
        if self.receiveSocket: self.receiveSocket.close()
        if self.controlSocket: self.controlSocket.close()
    def __del__(self):
        self.close()
    #### with statement ####
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return not exc_type # re-raise exception if any

    def send(self, *data):
        # print("Arg:", data)
        self.controlSocket.send(b'\x52'+b''.join(data))
    def reporting(self, mode=CONTINUOUS_REPORTING, extension=EXTENSION_8BYTES):
        byteExtension = struct.pack("B", extension)
        # print("byteExtension:", byteExtension)
        self.send(COMMAND_REPORTING, mode, byteExtension)
    def light(self, on_off=True):
        self.send(COMMAND_LIGHT, b'\x10' if on_off else b'\x00')
    def status(self):
        self.send(COMMAND_REQUEST_STATUS, b'\x00')

    def build_response(self, type, data):
        return {
            'type': type,
            'data': data
        }


# Initialize the board
wiiBoard = WiiBoard()
while 1:
    newImp = input("Trigger a board read\n")

    # Read the board
    response = wiiBoard.read_data()
    if (response != None):
        print("here")
        respType = response["type"]
        data = response["data"]
        print("Response type:", respType)
        if respType == ResponseType.STATUS:
            logger.info(f"{respType} - {data}")
        elif respType == ResponseType.CALIBRATION:
            logger.info(f"{respType} - {data}")
        elif respType == ResponseType.MASS:
            logger.info(f"{respType} - {data}")
    else:
        logger.info("No Response")

# Possible TODO: Check if we can change the frequency that the mass data is sent


# Wii Balance Board Docs -> https://wiibrew.org/wiki/Wii_Balance_Board