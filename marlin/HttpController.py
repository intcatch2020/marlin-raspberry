from flask import Flask, jsonify, make_response
from flask_classful import FlaskView, route
from marlin.Provider import Provider

VERSION = "0.0.1"


class HttpController(FlaskView):
    route_base = '/'
    boat = Provider().get_Boat()

    @route('/')
    def index(self):
        return make_response("OK<br>version: "+VERSION)

    @route('/state')
    def state(self):
        return jsonify(self.boat.get_state())

    @route('/start_autonomy')
    def start_autonomy(self):
        if self.boat.start_autonomy():
            return make_response('OK')
        else:
            return make_response('ERROR', 503)

    @route('/stop_autonomy')
    def stop_autonomy(self):
        if self.boat.stop_autonomy():
            return make_response('OK')
        else:
            return make_response('ERROR', 503)

    @route('/test/')
    def test(self):
        return 'test'


if __name__ == '__main__':
    h = HttpController()
    h.start()
