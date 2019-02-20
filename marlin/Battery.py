from marlin.Provider import Provider


class Battery:
    def __init__(self):
        self.value = 0
        self.unit = 'V'
        Provider().get_ArduinoSerialParser().add_sensor(
                'battery', self.update_value)

    def update_value(self, data):
        self.value = data['value']

    def get_state(self):
        return {'name': 'battery',
                'value': self.value,
                'unit': self.unit}
