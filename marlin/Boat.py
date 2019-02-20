import logging
import numpy as np

from marlin.MotorController import MotorController
from marlin.Provider import Provider
from marlin.BlueBox import BlueBoxSensor, SensorType, BlueBoxReader
from marlin.Battery import Battery


class Boat:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.GPS = Provider().get_GPS()
        self.APS = Provider().get_AbsolutePositionSensor()
        self.sensors = [BlueBoxSensor(SensorType.PH),
                        BlueBoxSensor(SensorType.DO),
                        BlueBoxSensor(SensorType.EC),
                        BlueBoxSensor(SensorType.DO_T),
                        Battery()]
        self.motor_controller = MotorController()
        self.autonomy = Provider().get_Autonomy()

    def get_state(self):
        state = {'sensors': [],
                 'GPS': self.GPS.state,
                 'APS': self.APS.state,
                 'driving_mode': self.motor_controller.driving_mode,
                 'autonomy_speed': self.autonomy.speed
                 }
        for sensor in self.sensors:
            sensor_state = sensor.get_state()
            if sensor_state is not None:
                state['sensors'].append(sensor_state)
        return state

    def start_autonomy(self, data):
        self.logger.debug(data)
        try:
            path = data['path']
            coordinates = []
            for coordinate in path:
                coordinates.append([coordinate['lat'], coordinate['lng']])
            self.autonomy.set_coordinates(np.array(coordinates))
            self.autonomy.start()
            return True
        except KeyError as e:
            self.logger.info(e)
            return False

    def stop_autonomy(self):
        self.autonomy.stop()
        return True

    def set_speed(self, data):
        try:
            speed = float(data['speed'])
            self.autonomy.set_speed(speed)
            return True
        except KeyError as e:
            self.logger.warning(e)
        except ValueError as e:
            self.logger.warning(e)
        return False
