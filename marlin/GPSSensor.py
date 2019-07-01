import logging
import gps
import time

from threading import Thread


class GPSSensor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = gps.gps("localhost", "2947")
        self.session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
        self.stop = False
        self.state = {'lng': -1, 'lat': -1, 'speed': 0, 'heading': 0}
        self.loop_thread = Thread(target=self.update_loop)
        self.loop_thread.start()

    def update_loop(self):
        while not self.stop:
            report = self.session.next()
            if hasattr(report, 'lon'):
                self.state['lng'] = report.lon
            if hasattr(report, 'lat'):
                self.state['lat'] = report.lat
            if hasattr(report, 'speed'):
                self.state['speed'] = report.speed
            if hasattr(report, 'track'):
                self.state['heading'] = report.track
            time.sleep(0.1)

    def stop(self):
        self.stop = True
        self.logging.info('closing GPS')
        self.loop_thread.join()
        self.session.close()
