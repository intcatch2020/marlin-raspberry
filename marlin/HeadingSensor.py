import logging 
import numpy as np 
import time
from threading import Thread
from marlin.utils import headingToVector
from marlin.Provider import Provider


class HeadingSensor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.GPS = Provider().get_GPS()
        self.APS = Provider().get_AbsolutePositionSensor()
        self.heading = 0


    def get_state(self):
        heading = self.APS.state['heading']
        return heading 