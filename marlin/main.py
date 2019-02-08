import time
import logging
import json


logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO,
                    handlers=[
                        logging.FileHandler("{0}/{1}.log".format('/tmp/', 'boat')),
                        logging.StreamHandler()])
logging.getLogger('Adafruit_BNO055.BNO055').setLevel(logging.INFO)

from marlin.Boat import Boat
from marlin.Provider import Provider
from flask import Flask, jsonify, make_response

boat = Provider().get_Boat()
app = Provider().get_HttpController()
app.run(port=5000, host='0.0.0.0')
time.sleep(100)
