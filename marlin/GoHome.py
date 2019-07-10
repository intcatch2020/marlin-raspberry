from threading import Thread
from collections import defaultdict
from simple_pid import PID
from marlin.Provider import Provider
from marlin.Astar import Node, A_star
from marlin.utils import headingToVector, directionError, clip

import utm
import time
import logging


class GoHome:
    UDPDATE_TIME_S = 1
    AUTOMATIC_START_S = 60

    def __init__(self, min_distance = 2):
        self.logger = logging.getLogger(__name__)
        self.grid_map = defaultdict(defaultdict(lambda: None))
        self.home = None
        self.running = False
        self.GPS = Provider().get_GPS()
        self.autonomy = Provider().get_Autonomy()
        self.RC = Provider().get_RC()
        self.pid_controller = PID(*self.pid)
        self.path = None
        self.off_timestamp = time.time()
        self.next_target = 0
        self.min_distance = min_distance
        self.stop = False

        self.loop_thread = Thread(target=self.update_loop)
        self.loop_thread.start()

    def update_loop(self):
        while not self.stop:
            boat_position = utm.from_latlon(self.GPS.state['lat'],
                                            self.GPS.state['lng'])[:2]
            x, y = round(boat_position[0]), round(boat_position[1])
            self.grid_map[x][y] = Node(x, y)
            self.check_automatic_start()
            time.sleep(time.time() % self.UDPDATE_TIME_S)

    def check_automatic_start(self):
        now = time.time()
        if self.RC.is_active or self.autonomy.is_active:
            return

        # if RC or autonomy was active less then AUTOMATIC_START_S seconds ago
        # don't start go_home
        if now - self.RC.off_timestamp < self.AUTOMATIC_START_S:
            return

        if now - self.autonomy.off_timestamp < self.AUTOMATIC_START_S:
            return

        if now - self.off_timestamp < self.AUTOMATIC_START_S:
            return

        self.next_target = 0
        self.path = self.calculate_path().node_list
        self.running = True

    def calculate_path(self):
        boat_position = utm.from_latlon(self.GPS.state['lat'],
                                        self.GPS.state['lng'])[:2]
        x, y = round(boat_position[0]), round(boat_position[1])
        start = Node(x, y)
        path = A_star(start, self.home, self.grid_map)
        return path

    def is_active(self):
        return self.running

    def stop(self):
        self.is_running = False
        self.path = None
        self.next_target = 0
        self.off_timestamp = time.time()

    def start(self):
        if self.running:
            return

        self.next_target = 0
        self.path = self.calculate_path().node_list
        self.running = True


    def get_state(self):
        # if not running or reached last point
        boat_position = utm.from_latlon(self.GPS.state['lat'],
                                        self.GPS.state['lng'])[:2]

        # select next waypoint
        while True:
            # check that boat is running and there are point left
            if not self.is_running or self.path is None or self.next_target >= len(self.path):
                self.logger.info('Last waypoint reached')
                self.stop()
                return {'trust': 0, 'turn': 0, 'scale': 0}

            # check if we reached waypoint
            waypoint = self.path[self.next_target]
            if pointDistance(boat_position, waypoint) > self.min_distance:
                break

            self.next_target += 1
            self.logger.debug('Reached target {}'.format(self.next_target-1))

        target_position = self.path[self.next_target]

        boat_direction = headingToVector(self.APS.state['heading'])
        #boat_direction = self.heading_sensor.get_state()['vector_heading']

        error = directionError(boat_position, target_position, boat_direction)
        correction = self.pid_controller(error)

        # if boat is point in opposite direction turn on the spot
        trust = 500*(1.0-error) if abs(error) < 0.5 else 0
        trust = trust * self.speed/100.0
        turn = 500 * clip(correction, -1, 1)
        return {'trust': trust, 'turn': turn, 'scale': 1}
