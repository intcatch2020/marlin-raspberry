import logging 
import numpy as np 
import time
from threading import Thread
from marlin.utils import headingToVector, KalmanFilter
from marlin.Provider import Provider


class HeadingSensor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.GPS = Provider().get_GPS()
        self.APS = Provider().get_AbsolutePositionSensor()

        F = np.array([[1]])
        B = np.array([[1]])
        H = np.array([[1]])
        Q = np.array([[0.01]]) # process noise covariance, and avoid P equal zero
        R = np.array([[10]]) # measurament covariance 
        P = np.array([[0.1]]) # process noise
        self.kf = KalmanFilter(F=F, B=B, H=H, Q=Q, R=R, P=P)
        self.old_heading = self.APS.state['heading']
        self.heading_setup = False


    def get_state(self):
        new_heading = self.APS.state['heading']

        # setup initial heading
        if not self.heading_setup and self.APS.state['mag_cal'] == 3:
            self.kf.x = np.array([[new_heading]])
            self.heading_setup = True
            self.old_heading = new_heading
            return new_heading

        # calculate heading using kalman filter
        heading = self.kf.predict(new_heading - self.old_heading)[0][0]
        self.old_heading = new_heading
        
        # normalize heading
        heading = heading % 360
        self.kf.x = np.array([[heading]])


        # adjust kalman filter using GPS heading if boat is moving
        if self.GPS.state['speed'] > 1.0:
            gps_heading = self.GPS.state['heading']
            if gps_heading - heading > 180:
                gps_heading -= 360
            if gps_heading - heading < -180:
                gps_heading += 360

            self.kf.update(np.array([[gps_heading]]))

        return heading 