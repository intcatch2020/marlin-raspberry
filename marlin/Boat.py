import logging
import numpy as np

from marlin.MotorController import MotorController
from marlin.Provider import Provider
from marlin.BlueBox import BlueBoxSensor, SensorType
from marlin.BlueBox import BlueBoxPump


class Boat:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        #  self.GPS = Provider().get_GPS()
        #  self.APS = Provider().get_AbsolutePositionSensor()
        self.sensors = [BlueBoxSensor(SensorType.PH),
                        BlueBoxSensor(SensorType.DO),
                        BlueBoxSensor(SensorType.EC),
                        BlueBoxSensor(SensorType.DO_T)]
        self.pump = BlueBoxPump()
        #  self.motor_controller = MotorController()
        #  self.autonomy = Provider().get_Autonomy()

    def get_state(self):
        import random
        state = {'sensors': [],
                 #  'GPS': self.GPS.state,
                 #  'APS': self.APS.state,
                 #  'driving_mode': self.motor_controller.driving_mode,
                 #  'autonomy_speed': self.autonomy.speed
                 }

        for sensor in self.sensors:
            sensor_state = sensor.get_state()
            if sensor_state is not None:
                state['sensors'].append(sensor_state)

        state['sensors'].append(
                {'name': 'battery', 'unit': 'V', 'value': 15})

        if self.pump is not None:
            state['pump'] = self.pump.get_state()

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

    def set_pump(self, data):
        if self.pump is None:
            return True

        try:
            active = data['pump_on']
            timer = data['pump_time']
            self.pump.set_timer(timer)
            self.pump.set_pump_state(active)
            return True
        except KeyError as e:
            self.logger.warning(e)
        except ValueError as e:
            self.logger.warning(e)
        return False
