import logging
import numpy as np

from marlin.MotorController import MotorController
from marlin.Provider import Provider


class Boat:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.motor_controller = MotorController()
        self.GPS = Provider().get_GPS()
        self.APS = Provider().get_AbsolutePositionSensor()
        self.autonomy = Provider().get_Autonomy()

    def get_state(self):
        import random
        ph = random.uniform(3, 10)
        do = random.uniform(10, 40)
        ec = random.uniform(700, 1200)
        battery = random.uniform(14, 16)
        state = {'sensors': {'ph': ph, 'do': do, 'ec': ec},
                 'GPS': self.GPS.state,
                 'APS': self.APS.state,
                 'battery': battery
                 }
        return state

    def start_autonomy(self, data):
        self.logger.debug(data)
        try:
            path = data['path']
            coordinates = []
            for coordinate in path:
                coordinates.append([coordinates['lng'], coordinates['lat']])
            self.autonomy.set_coordinates(np.array(coordinates))
            self.autonomy.start()
            return True
        except KeyError as e:
            self.logger.info(e)
            return False

    def stop_autonomy(self):
        self.autonomy.stop()
        return True
