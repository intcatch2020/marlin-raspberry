import argparse
import time
import logging
import json
import os
from marlin.utils import delete_old_log, get_log_name
from marlin.Boat import Boat
from marlin.Provider import Provider
from marlin.DataLogger import DataLogger
from flask import Flask, jsonify, make_response


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--debug', dest='debug', action='store_true', default=False)
    config = parser.parse_args()

    DATA_FOLDER = '/var/marlin/data'
    DATA_FILE = os.path.join(DATA_FOLDER, get_log_name())
    LOG_FOLDER = '/var/marlin/log'
    LOG_LEVEL = logging.INFO if not config.debug else logging.DEBUG
    LOG_FILE = os.path.join(LOG_FOLDER, get_log_name())
    LOG_FORMAT = '%(asctime)-15s  %(levelname)-8s %(name)s: %(message)s'

    os.makedirs(DATA_FOLDER, exist_ok=True)
    os.makedirs(LOG_FOLDER, exist_ok=True)
    delete_old_log(LOG_FOLDER)
    delete_old_log(DATA_FOLDER)

    # add log to console and file
    marlinFormatter = logging.Formatter(LOG_FORMAT)
    marlinFileHandler = logging.FileHandler(filename=LOG_FILE, mode='w')
    marlinFileHandler.setFormatter(marlinFormatter)
    marlinConsoleHandler = logging.StreamHandler()
    marlinConsoleHandler.setFormatter(marlinFormatter)

    logging.getLogger('marlin').addHandler(marlinConsoleHandler)
    logging.getLogger('marlin').addHandler(marlinFileHandler)
    logging.getLogger('marlin').setLevel(LOG_LEVEL)

    dataFormatter = logging.Formatter(LOG_FORMAT)
    dataFileHandler = logging.FileHandler(filename=DATA_FILE, mode='w')
    dataFileHandler.setFormatter(dataFormatter)
    logging.getLogger('data').addHandler(dataFileHandler)
    logging.getLogger('data').setLevel(logging.INFO)

    boat = Provider().get_Boat()
    dataLogger = DataLogger()

    # HTTP
    app = Provider().get_HttpController()
    app.run(port=5000, host='0.0.0.0')

    # SocketIO
    # socket = Provider().get_SocketClient()
    # socket.start()

if __name__ == "__main__":
    main()
