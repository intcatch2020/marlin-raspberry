import socketio
import time
from threading import Thread

from marlin.Provider import Provider

class SocketController(socketio.ClientNamespace):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.boat = Provider().get_Boat()
        self.is_connected = False
        self.update_state_thread = Thread(target=self.update_loop)

    def on_connect(self):
        self.emit('register_boat')
        self.is_connected = True
        if not self.update_state_thread.is_alive():
            self.update_state_thread.start()

    def on_start_autonomy(self, data):
        self.boat.start_autonomy(data)

    def on_stop_autonomy(self, data):
        self.boat.stop_autonomy()

    def on_set_speed(self, data):
        self.boat.set_speed(data)
    
    def on_disconnect(self):
        self.is_connected = False
    
    def update_loop(self):
        while(True):
            if self.is_connected:
                self.emit('state', self.boat.get_state())
            time.sleep(1)

class SocketIOClient():
    def __init__(self, ip='localhost', port=5000):
        self.sio = socketio.Client()
        self.sio.register_namespace(SocketController())
        self.sio.connect('http://{}:{}'.format(ip, port))
    
    def start(self):
        self.sio.wait()


