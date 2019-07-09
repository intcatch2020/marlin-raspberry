import logging

from singleton_decorator import singleton
from flask import Flask, jsonify, make_response


@singleton
class Provider:
    def __init__(self):
        self.instances = {}

    def get_ArduinoSerialParser(self):
        from marlin.ArduinoSerialReader import ArduinoSerialReader
        return self._get_instace('ArduinoSerialReader', ArduinoSerialReader,
                                 '/dev/arduino')

    def get_RC(self):
        from marlin.RCPi import RCPi
        return self._get_instace('RC', RCPi, '/dev/rc')

    def get_GPS(self):
        from marlin.GPSSensor import GPSSensor
        return self._get_instace('GPS', GPSSensor)

    def get_heading(self):
        from marlin.HeadingSensor import HeadingSensor
        return self._get_instace('heading', HeadingSensor)

    def get_AbsolutePositionSensor(self):
        from marlin.AbsolutePositionSensor import AbsolutePositionSensor
        return self._get_instace(
                'APS', AbsolutePositionSensor, '/dev/serial0', 18)

    def get_ACS(self):
        from marlin.acs import ACS
        return self._get_instace('ACS', ACS)

    def get_Boat(self):
        from marlin.Boat import Boat
        return self._get_instace('Boat', Boat)

    def get_HttpController(self):
        from marlin.HttpController import HttpController
        app = Flask(__name__)
        HttpController.register(app)
        return app

    def get_SocketClient(self):
        from marlin.WebSocketController import SocketIOClient
        return self._get_instace('socketClient',
                                 SocketIOClient,
                                 'localhost',
                                 5000)

    def get_Autonomy(self):
        from marlin.Autonomy import Autonomy
        return self._get_instace('Autonomy', Autonomy)

    def get_BlueBoxReader(self):
        from marlin.BlueBox import BlueBoxReader
        return self._get_instace(
                'BlueBoxReader', BlueBoxReader)

    def _get_instace(self, key, cls, *args, **kwargs):
        if key not in self.instances:
            self.instances[key] = cls(*args, **kwargs)

        return self.instances[key]

    def close(self):
        if 'ArduinoSerialReader' in self.instances:
            self.instances['ArduinoSerialReader'].close()

