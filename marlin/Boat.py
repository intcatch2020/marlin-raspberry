import logging

from marlin.MotorController import MotorController
from marlin.Provider import Provider


class Boat:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.motor_controller = MotorController()
        self.GPS = Provider().get_GPS()
        self.APS = Provider().get_AbsolutePositionSensor()

    def get_state(self):
        import random
        ph = random.uniform(3, 10)
        do = random.uniform(10, 40)
        ec = random.uniform(700, 1200)
        battery = random.uniform(14, 16)
        state = {'sensors': {'ph': ph, 'DO': do, 'EC': ec},
                 'GPS': self.GPS.state,
                 'APS': self.APS.state,
                 'battery': battery
                 }
        return state

    def start_autonomy(self):
        return True

    def stop_autonomy(self):
        return False
