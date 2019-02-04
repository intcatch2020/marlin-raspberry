import logging
import numpy as np
import utm

from marlin.Provider import Provider
from marlin.utils import closestPointOnLine, directionError
from marlin.utils import clip, headingToVector
from simple_pid import PID


class Autonomy:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.is_running = False
        self.pid = (-1, 0, 0.5)
        self.coordinates = np.array([])
        self.next_target = 0
        self.loop_thread = None
        self.pid_controller = PID(*self.pid)
        self.GPS = Provider().get_GPS()
        self.APS = Provider().get_AbsolutePositionSensor()
        self.offset = 1
        self.speed = 30

    def set_coordinates(self, coordinates):
        boat_position = utm.from_latlon(self.GPS.state['lat'],
                                        self.GPS.state['lng'])[:2]
        self.coordinates = [boat_position]
        for lat, lng in coordinates:
            c = utm.from_latlon(lat, lng)[:2]
            self.coordinates.append(c)

        self.coordinates = np.array(coordinates)
        self.next_target = 1

    def set_pid(self, pid):
        self.pid = pid

    def set_speed(self, speed):
        self.speed = speed

    def start(self):
        boat_position = utm.from_latlon(self.GPS.state['lat'],
                                        self.GPS.state['lng'])[:2]

        # if we need to go to first waypoint create line from current position
        # to the waypoint
        if self.next_target == 1:
            self.coordinates[0] = boat_position

        self.is_running = True
        self.pid_controller = PID(*self.pid)

    def stop(self):
        self.is_running = False

    def is_active(self):
        return self.is_running

    def get_state(self):
        # if not runninf or reached last point

        boat_position = utm.from_latlon(self.GPS.state['lat'],
                                        self.GPS.state['lng'])[:2]

        # if next point is close the boat, reapeat this with successive point
        while True:
            # check that boat is running and there are point left
            if not self.is_running or self.next_target >= len(self.coordinates):
                self.logger.info('Last waypoint reached')
                self.is_running = False
                return {'trust': 0, 'turn': 0, 'scale': 0}

            # take first two points
            i = min(self.next_target, 1)
            target_position, line_fraction = closestPointOnLine(
                    self.coordinates[i-1],
                    self.coordinates[i],
                    boat_position, 1)

            # if boat reached point move the the next one and repeat
            if line_fraction > 1:
                self.next_target += 1
            else:
                break

        boat_direction = headingToVector(self.APS.state['heading'])
        self.logger.debug(
            'position: {} direction: {} waypoint: {}, number {}'.format(
                boat_position, boat_direction, self.coordinates[i], i))

        error = directionError(boat_position, target_position, boat_direction)
        correction = self.pid_controller(error)

        # if boat is point in opposite direction turn on the spot
        trust = 500 if abs(error) < 1 else 0
        turn = 500 * clip(correction, -1, 1)
        return {'trust': trust, 'turn': turn, 'scale': self.speed/100}
