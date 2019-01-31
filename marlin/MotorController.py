import logging
import time

from marlin.Provider import Provider
from marlin.utils import clip
from threading import Thread

RIGHT_MOTOR_PIN = 17
LEFT_MOTOR_PIN = 27
MAX_SPEED = 2000
MIN_SPEED = 1000
IS_PI = False

if IS_PI:
    import pigpio


class MotorController:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.left_motor = None
        self.right_motor = None
        self.controllers = [Provider().get_RC(), Provider().get_Autonomy()]
        self.Autonomy = None  # Provider.getAutonomy
        if IS_PI:
            self.pi = pigpio.pi()
        self.on = False
        self.stop = False
        self.setup()
        self.turn_on()
        self.loop_thread = Thread(target=self.update_loop)
        self.loop_thread.start()

    def setup(self):
        if IS_PI:
            self.pi.set_mode(RIGHT_MOTOR_PIN, pigpio.OUTPUT)
            self.pi.set_mode(LEFT_MOTOR_PIN, pigpio.OUTPUT)
            self.pi.set_pull_up_down(RIGHT_MOTOR_PIN, pigpio.PUD_OFF)
            self.pi.set_pull_up_down(LEFT_MOTOR_PIN, pigpio.PUD_OFF)

    def set_engine_state(self, speed, turn, scale):
        self.logger.debug('speed: {}, turn: {}, scale: {}'.format(
            speed, turn, scale))

        l_speed = r_speed = speed
        l_speed += turn / 2
        r_speed -= turn / 2

        offset = 0
        top_limit = max(l_speed, r_speed)
        bottom_limit = min(l_speed, r_speed)

        if top_limit > 500:
            offset = top_limit - 500
        if bottom_limit < -500:
            offset = bottom_limit + 500

        l_speed = (l_speed - offset) * scale + 1500
        r_speed = (r_speed - offset) * scale + 1500
        l_speed = clip(l_speed, 1000, 2000)
        r_speed = clip(r_speed, 1000, 2000)

        self.logger.debug(
            'l_speed: {}, r_speed: {}, offset: {}, scale: {}'.format(
                l_speed, r_speed, offset, scale))

        if IS_PI:
            self.pi.set_servo_pulsewidth(LEFT_MOTOR_PIN, l_speed)
            self.pi.set_servo_pulsewidth(RIGHT_MOTOR_PIN, r_speed)

    def turn_on(self):
        if IS_PI:
            self.pi.set_servo_pulsewidth(RIGHT_MOTOR_PIN, 1500)
            self.pi.set_servo_pulsewidth(LEFT_MOTOR_PIN, 1500)

        # wait 2 second for motors to start
        time.sleep(2)
        self.on = True

    def update_loop(self):
        while not self.stop:
            active_controller = False
            for controller in self.controllers:
                if controller.is_active():
                    state = controller.get_state()
                    self.set_engine_state(state['trust'],
                                          state['turn'],
                                          state['scale'])
                    active_controller = True
            if not active_controller:
                    self.set_engine_state(0, 0, 0)
            time.sleep(1)
