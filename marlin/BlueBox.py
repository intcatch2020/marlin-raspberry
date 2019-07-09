import logging
import serial
import socket
import time
import os

from enum import Enum
from threading import Thread
from marlin.utils import SensorExistsException
from marlin.Provider import Provider

class BlueBoxReader:
    def __init__(self, ip='localhost', port=2948, timeout=5):
        self.logger = logging.getLogger(__name__)
        self.sensors = {}
        self.stop = False
        self.ip = ip
        self.port = port

        try:
            self.socket_connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_connection.connect((self.ip, self.port))
        except ConnectionRefusedError:
            self.logger.warning('BlueBox connection refused at ip {} port {}'.format(self.ip, self.port))
            return


        self.loop_thread = Thread(target=self._read_loop)
        self.loop_thread.start()
        self.logger.info('BlueBox OK')

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
        buffer = ''
        while not self.stop:
            if '\n' in buffer:
                line, buffer = buffer.split('\n', 1)
                print('line', line)
                try:
                    data = line.split(',')
                    sensor_name, sensor, value, unit = data[3:7]
                    self._notify_sensor(sensor_name, float(value))
                except IndexError as e:
                    self.logger.debug(e)
                except ValueError as e:
                    self.logger.debug(e)
                except TypeError as e:
                    self.logger.debug(e)
            else:
                more = self.socket_connection.recv(4096).decode('cp1252')
                if more:
                    buffer += more

    def write(self, data):
        if data[-1] != '\n':
            data += '\n'
        self.serial_connection.write(data.encode())

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
    DO = 'O2'
    DO_T = 'Temperature'
    Pressure = 'Pressure'


class BlueBoxSensor:
    UNITS = {SensorType.PH: 'mg/l',
             SensorType.EC: 'uS',
             SensorType.EC_T: 'C',
             SensorType.DO_T: 'C',
             SensorType.DO: 'mg/l',
             SensorType.Pressure: 'bar'}

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


class BlueBoxPump:
    def __init__(self):
        self.speed = 0
        self.active = False
        self.bluebox = Provider().get_BlueBoxReader()
        self.bluebox.add_sensor('Pumpe 1', self.update_speed)
        self.timer = 0

    def update_speed(self, speed):
        self.speed = speed
        self.check_timer()
        if self.active != bool(self.speed):
            self.set_pump_state(self.active)

    def check_timer(self):
        if self.timer != 0 and self.timer < time.time():
            self.active = False
            self.timer = 0

    def set_timer(self, duration_sec):
        if duration_sec == 0:
            self.timer = 0
            return
        self.timer = time.time() + duration_sec

    def set_pump_state(self, active):
        self.active = bool(active)
        self.bluebox.write('$PGO02,pump_on,{}\n'.format(int(self.active)))

    def get_state(self):
        return {'active': self.active,
                'speed': self.speed,
                'time': max(0, self.timer - time.time())}


if __name__ == '__main__':
    import time
    ss = [BlueBoxSensor(SensorType.PH), BlueBoxSensor(SensorType.DO),
          BlueBoxSensor(SensorType.EC), BlueBoxSensor(SensorType.EC_T),
          BlueBoxSensor(SensorType.DO_T), BlueBoxPump()]
    ss[-1].set_pump_state(True)
    ss[-1].set_timer(20)
    while 1:
        for s in ss:
            print(s.get_state())
        time.sleep(1)
