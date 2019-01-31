import logging
import gps

from threading import Thread


class GPSSensor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.session = gps.gps("localhost", "2947")
        self.session.stream(gps.WATCH_ENABLE | gps.WATCH_NEWSTYLE)
        self.stop = False
        self.state = {'lng': '11.02', 'lat': '45.35', 'speed': 0}
        self.loop_thread = Thread(target=self.update_loop)
        self.loop_thread.start()

    def update_loop(self):
        while not self.stop:
            report = self.session.next()
            self.logger.debug(report)
            if hasattr(report, 'lon'):
                self.state['lng'] = report.lon
            if hasattr(report, 'lat'):
                self.state['lat'] = report.lat
            if hasattr(report, 'speed'):
                self.state['speed'] = report.speed

    def stop(self):
        self.stop = True
        self.logging.info('closing GPS')
        self.loop_thread.join()
        self.session.close()
