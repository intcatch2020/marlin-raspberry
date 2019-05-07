import logging
import serial

from bitstring import BitArray, InterpretError
from marlin.utils import clip


class RCPi:
    def __init__(self, port):
        self.logger = logging.getLogger(__name__)
        self.name = 'RC'
        self.port = port
        self.state = {
            'trust': 0,  # throttle (1000-2000)
            'turn': 0,  # turn (1000-2000)
            'override': True,  # RC override
            'scale': 0,  # throttle scale (0-1)
        }
        self.serial = serial.Serial(port=port,
                                    baudrate=100000,
                                    bytesize=serial.EIGHTBITS,
                                    parity=serial.PARITY_EVEN,
                                    stopbits=serial.STOPBITS_ONE)

    def _get_last_frame(self):
        data = self.serial.read_all()
        bits = BitArray(data)
        frames = list(bits.findall(BitArray(hex='000f')))
        if len(frames) < 2:
            return
        return bits[frames[-2]:frames[-1]]

    def _read_data(frame):
        if frame is None:
            return
        chs = {}
        bytes_data = [frame[i*8:(i+1)*8] for i in range(2, 24)]

        try:
            chs[0] = bytes_data[0].uint | bytes_data[1].uint << 8 & 2047
            chs[1] = bytes_data[1].uint >> 3 | bytes_data[2].uint << 5 & 2047
            chs[2] = bytes_data[2].uint >> 6 | bytes_data[3].uint << 3 \
                | bytes_data[4].uint << 10 & 2047
            chs[3] = bytes_data[4].uint >> 1 | bytes_data[5].uint << 7 & 2047
        except InterpretError:
            return

        return chs

    def rc_to_motor_signal(x):
        signal = (x - 990) * 0.61

        # remove noise from rest position
        if abs(signal) < 6:
            signal = 0

        # ensure value between -500 and 500
        return clip(signal, -500, 500)

    def get_state(self):
        data = RCPi._read_data(self._get_last_frame())

        if data is not None:
            self.state['trust'] = RCPi.rc_to_motor_signal(data[0])
            self.state['turn'] = RCPi.rc_to_motor_signal(data[1])
            self.state['override'] = data[2] > 990
            self.state['scale'] = min((data[3] - 172) * 0.00061, 1)

        return self.state

    def is_active(self):
        return self.state['override']


if __name__ == '__main__':
    import time
    rc = RCPi('/dev/ttyUSB0')
    for i in range(100):
        print(rc.get_state())
        time.sleep(0.1)
    
