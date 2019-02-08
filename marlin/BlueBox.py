import logging
import serial

from enum import Enum
from threading import Thread
from marlin.utils import SensorExistsException
from marlin.Provider import Provider


class BlueBoxReader:
    def __init__(self, serial_port, boud_rate=38400, timeout=5):
        self.logger = logging.getLogger(__name__)
        self.serial_port = serial_port
        self.boud_rate = boud_rate
        self.serial_connection = serial.Serial(
            self.serial_port, self.boud_rate, timeout=timeout)
        self.sensors = {}

        self.stop = False
        self.loop_thread = Thread(target=self._read_loop)
        self.loop_thread.start()

    def add_sensor(self, sensor_name, callback):
        if sensor_name in self.sensors:
            raise SensorExistsException(sensor_name)

        self.sensors[sensor_name.lower()] = callback

    def remove_sensor(self, sensor_name):
        if sensor_name in self.sensors:
            del self.sensors[sensor_name]
        else:
            self.logger.info('{} not register'.format(sensor_name))

    def _notify_sensor(self, sensor_name, data):
        try:
            self.sensors[sensor_name.lower()](data)
        except KeyError:
            pass

    def _read_loop(self):
        line = ''
        while not self.stop:
            try:
                line = self.serial_connection.readline().decode('cp1252')
                data = line.split(',')
                sensor_name, sensor, value, unit = data[3:7]
                self._notify_sensor(sensor_name, float(value))
            except IndexError as e:
                self.logger.debug(e)
            except ValueError as e:
                self.logger.debug(e)
            except TypeError as e:
                self.logger.debug(e)

    def close(self):
        self.stop = True
        self.logger.info('waiting for serial to close')
        self.serial_connection.close()
        self.loop_thread.join(timeout=60)
        if self.loop_thread.is_alive():
            self.logger.info('failed to close serial connection')
        else:
            self.logger.info('serial connection closed')


class SensorType(Enum):
    PH = 'pH'
    EC = 'Conductivity'
    EC_T = 'Temperature EC'
    DO = 'Oxygen'
    DO_T = 'Temperature O2'


class BlueBoxSensor:
    UNITS = {SensorType.PH: 'mg/l',
             SensorType.EC: 'uS',
             SensorType.EC_T: 'C',
             SensorType.DO_T: 'C',
             SensorType.DO: 'mg/l'}

    def __init__(self, sensor_type):
        self.value = None
        self.type = sensor_type
        self.unit = self.UNITS[self.type]
        Provider().get_BlueBoxReader().add_sensor(
                self.type.value, self.update_state)

    def update_state(self, value):
        self.value = value

    def get_state(self):
        if self.value is None:
            return

        return {'name': self.type.name,
                'value': self.value,
                'unit': self.unit}


if __name__ == '__main__':
    import time
    ss = [BlueBoxSensor(SensorType.PH), BlueBoxSensor(SensorType.DO),
            BlueBoxSensor(SensorType.EC), BlueBoxSensor(SensorType.EC_T),
            BlueBoxSensor(SensorType.DO_T)]
    while 1:
        for s in ss:
            print(s.get_state())
        time.sleep(1)


