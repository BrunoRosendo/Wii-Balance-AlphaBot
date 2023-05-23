import time
import logging
from WiiBoard import ResponseType, WiiBoard

# initialize the logger
logger = logging.getLogger(__name__)
handler = logging.StreamHandler() # or RotatingFileHandler
handler.setFormatter(logging.Formatter('[%(asctime)s][%(name)s][%(levelname)s] %(message)s'))
logger.addHandler(handler)
logger.setLevel(logging.INFO) # or DEBUG

# Initialize the board
wiiBoard = WiiBoard()
while 1:
    newImp = input("Trigger a board read\n")

    # Read the board
    response = wiiBoard.read_data()
    if (response != None):
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
