import argparse
import time
import logging
import json
import os
from marlin.utils import delete_old_log, get_log_name
from marlin.Boat import Boat
from marlin.Provider import Provider
from flask import Flask, jsonify, make_response


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', dest='debug', action='store_true', default=False)
    config = parser.parse_args()

    LOG_FOLDER = '/var/marlin/log'
    LOG_LEVEL = logging.INFO if not config.debug else logging.DEBUG
    LOG_FILE = os.path.join(LOG_FOLDER, get_log_name())
    LOG_FORMAT = '%(asctime)-15s  %(levelname)-8s %(name)s: %(message)s'

    os.makedirs(LOG_FOLDER, exist_ok=True)
    delete_old_log(LOG_FOLDER)

    logging.basicConfig(level=logging.WARNING,
                        filename=LOG_FILE,
                        filemode='w',
                        format=LOG_FORMAT)

    # add log to console
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(LOG_FORMAT))
    logging.getLogger('').addHandler(console)

    logging.getLogger('marlin').setLevel(LOG_LEVEL)
    # logging.getLogger('Adafruit_BNO055.BNO055').setLevel(logging.INFO)
    # logging.getLogger('werkzeug').setLevel(logging.WARNING)
    # logging.getLogger('socketio.client').setLevel(logging.WARNING)
    # logging.getLogger('engineio.client').setLevel(logging.WARNING)
    # logging.getLogger('requests').setLevel(logging.INFO)

    boat = Provider().get_Boat()

    # HTTP
    # app = Provider().get_HttpController()
    # app.run(port=5001, host='0.0.0.0')

    # SocketIO
    socket = Provider().get_SocketClient()
    socket.start()

if __name__ == "__main__":
    main()