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

# initialize the logger
logger = logging.getLogger(__name__)
handler = logging.StreamHandler() # or RotatingFileHandler
handler.setFormatter(logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s] %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.DEBUG) # or DEBUG

def join_packet_bytes(bytes):
    '''
    Joins the bytes of a packet 2 by 2
    '''
    return [bytes[j: j+2] for j in [0, 2, 4, 6]]

def discover(duration=6, prefix=BLUETOOTH_NAME):
    logger.info("Scan Bluetooth devices for %i seconds...", duration)
    devices = bluetooth.discover_devices(duration=duration, lookup_names=True)
    logger.debug("Found devices: %s", str(devices))
    return [address for address, name in devices if name.startswith(prefix)]

class Wiiboard:
    def __init__(self, address=None):
        self.controlSocket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_L2CAP)
        self.receiveSocket = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_L2CAP)
        self.calibration = [[1e4]*4]*3
        self.calibration_requested = False
        self.light_state = False
        self.button_down = False
        self.battery = 0.0
        self.running = True
        if address is not None:
            self.connect(address)
    def connect(self, address):
        logger.info("Connecting to %s", address)
        self.controlSocket.connect((address, 0x11))
        self.receiveSocket.connect((address, 0x13))
        logger.info("Connected sockets")

        logger.debug("Sending mass calibration request")
        self.send(COMMAND_READ_REGISTER, b"\x04\xA4\x00\x24\x00\x18")
        self.calibration_requested = True
        logger.info("Wait for calibration")

        logger.debug("Connect to the balance extension, to read mass data")
        self.send(COMMAND_REGISTER, b"\x04\xA4\x00\x40\x00")
        logger.debug("Request status")

        self.status()
        self.light(False)
    # *args accepts any number of arguments
    def send(self, *data):
        # print("Arg:", data)
        self.controlSocket.send(b'\x52'+b''.join(data))
    def sendIntData(self, intData):
        # convert data to bytes
        data = int.to_bytes(intData, byteorder='big')
        
        self.controlSocket.send(b'\x52'+b''.join(data))
    def reporting(self, mode=CONTINUOUS_REPORTING, extension=EXTENSION_8BYTES):
        byteExtension = struct.pack("B", extension)
        # print("byteExtension:", byteExtension)
        self.send(COMMAND_REPORTING, mode, byteExtension)
    def light(self, on_off=True):
        self.send(COMMAND_LIGHT, b'\x10' if on_off else b'\x00')
    def status(self):
        self.send(COMMAND_REQUEST_STATUS, b'\x00')
        
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
        # print("[Calc_Mass]raw:", raw, "rawType:", type(raw))

        # convert raw data (bytes) to int

        parsed_mass_aux = raw[0:2]
        # print("parsed_mass_aux", parsed_mass_aux)

        parsed_mass = int.from_bytes(parsed_mass_aux, byteorder='big')
        # print("[Calc_Mass] parsed_mass:", parsed_mass)

        # Check the hexadecimal value of raw data (2 int format)
        # parsed_mass_split = [parsed_mass_aux[i] for i in range(len(parsed_mass_aux))]
        # print("[Calc_Mass] parsed_mass_split:", parsed_mass_split)
        
        # Convert Calibration data to int and extract the data from a specific pos
        calibration = [ int.from_bytes( [self.calibration[i][pos][j] for j in range(len(self.calibration[i][pos])) ], byteorder="big") for i in range(len(self.calibration)) ]
        # print("[Calc_Mass] Calibration:", calibration)
        
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
    def check_button(self, state):
        if state == BUTTON_DOWN_MASK:
            if not self.button_down:
                self.button_down = True
                self.on_pressed()
        elif self.button_down:
            self.button_down = False
            self.on_released()
    def get_mass(self, data):
        # print("[Get_Mass] data:", data)
        mass_data = [data[i] for i in range(len(data))]
        # print("[Get_Mass] mass_data:", mass_data)
        return  {
            'top_right':    self.calc_mass(data[0:2], TOP_RIGHT),
            'bottom_right': self.calc_mass(data[2:4], BOTTOM_RIGHT),
            'top_left':     self.calc_mass(data[4:6], TOP_LEFT),
            'bottom_left':  self.calc_mass(data[6:8], BOTTOM_LEFT),
        }
    def loop(self):
        logger.debug("Starting the receive loop")
        while self.running and self.receiveSocket:
            data = self.receiveSocket.recv(25)
            # logger.debug("socket.recv(25): %r", data)
            if len(data) < 2:
                continue
            
            """ hexCodes = [int(data.hex()[i:i+2], 16) for i in range(0, len(data.hex()), 2)]
            input_type = hexCodes[1]

            print("hexCodes", hexCodes)
            print("input_type", input_type) """

            byteCodes = [int(data[i]) for i in range(0, len(data))]
            # print("byteCodes", byteCodes, len(data))
            input_type = data[1] 

            print("input_type", input_type)
            if input_type == INPUT_STATUS:
                batteryLevel = data[7]  # Get byte 7 from the packet
                print("[INPUT_TYPE] batteryLevel", batteryLevel)
                self.battery = batteryLevel / BATTERY_MAX
                # 0x12: on, 0x02: off/blink
                # print("[INPUT_TYPE] data[4]", data[4])
                self.light_state = data[4] & LED1_MASK == LED1_MASK
                self.on_status()
            elif input_type == INPUT_READ_DATA:
                logger.debug("Got calibration data")
                if self.calibration_requested:
                    # print("[INPUT_READ_DATA] data[4]", data[4])
                    length = int(data[4] / 16 + 1)
                    # print("[INPUT_READ_DATA] length:", length)
                    data = data[7:7 + length]
                    cal = lambda d: [d[j:j+2] for j in [0, 2, 4, 6]]
                    if length == 16: # First packet of calibration data
                        self.calibration = [cal(data[0:8]), cal(data[8:16]), [1e4]*4]
                    elif length < 16: # Second packet of calibration data
                        self.calibration[2] = cal(data[0:8])
                        self.calibration_requested = False
                        self.on_calibrated()
            elif input_type == EXTENSION_8BYTES:
                print("[EXTENSION] EXTENSION_8BYTES")
                self.check_button(data[2:4])
                massVal = self.get_mass(data[4:12])
                self.on_mass(massVal)
    def on_status(self):
        self.reporting() # Must set the reporting type after every status report
        logger.info("Status: battery: %.2f%% light: %s", self.battery*100.0,
                    'on' if self.light_state else 'off')
        self.light(1)
    def on_calibrated(self):
        logger.info("Board calibrated: %s", str(self.calibration))
        self.light(1)
    def on_mass(self, mass):
        print("[ON_MASS] mass:", mass)
        logger.debug("New mass data: %s", str(mass))
    def on_pressed(self):
        logger.info("Button pressed")
    def on_released(self):
        logger.info("Button released")
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

class WiiboardSampling(Wiiboard):
    def __init__(self, address=None, nsamples=N_SAMPLES):
        Wiiboard.__init__(self, address)
        self.samples = collections.deque([], nsamples)
    """
    # TODO: Check wtf is this 
    def on_mass(self, mass):
        self.samples.append(mass)
        self.on_sample()
    def on_sample(self):
        time.sleep(0.01) """

# client class where we can re-define callbacks
class WiiboardPrint(WiiboardSampling):
    def __init__(self, address=None, nsamples=N_SAMPLES):
        WiiboardSampling.__init__(self, address, nsamples)
        self.nloop = 0
    def on_sample(self):
        if len(self.samples) == N_SAMPLES:
            samples = [sum(sample.values()) for sample in self.samples]
            print("%.3f %.3f"%(time.time(), sum(samples) / len(samples)))
            self.samples.clear()
            self.status() # Stop the board from publishing mass data
            self.nloop += 1
            if self.nloop > N_LOOP:
                return self.close()
            self.light(0)
            time.sleep(T_SLEEP)

if __name__ == '__main__':
    import sys
    if '-d' in sys.argv:
        logger.setLevel(logging.DEBUG)
        sys.argv.remove('-d')
    if len(sys.argv) > 1:
        address = sys.argv[1]
    else:
        wiiboards = discover()
        logger.info("Found wiiboards: %s", str(wiiboards))
        if not wiiboards:
            raise Exception("Press the red sync button on the board")
        address = wiiboards[0]
    with WiiboardPrint(address) as wiiprint:
        wiiprint.loop()