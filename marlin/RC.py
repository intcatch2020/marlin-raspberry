import logging
import math

from marlin.Provider import Provider
from marlin.utils import clip


class RC:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.asp = Provider().get_ArduinoSerialParser()
        self.asp.add_sensor('RC', self.set_state)
        self.listeners = set()
        self.state = {
            'trust': 1500,  # throttle (1000-2000)
            'turn': 1500,  # turn (1000-2000)
            'override': True,  # RC override
            'scale': 1,  # throttle scale (0-1)
        }

    def set_state(self, data):
        self.logger.debug(data)
        try:
            self.state['trust'] = RC.rc_to_motor_signal(data['trust'])
            self.state['turn'] = RC.rc_to_motor_signal(data['turn'])
            self.state['override'] = data['override'] > 990
            self.state['scale'] = min((data['max_power'] - 172) * 0.00061, 1)
        except KeyError as e:
            self.logger.debug(e)

    def rc_to_motor_signal(x):
        # ensure value between -500 and 500
        signal = (x - 990) * 0.61

        # remove noise from rest position
        if abs(signal) < 6:
            signal = 0

        return clip(signal, -500, 500)