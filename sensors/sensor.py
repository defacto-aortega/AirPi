

class Sensor:
    requiredOptions = []
    optionalOptions = []

    def __init__(self,data):
        raise NotImplementedError

    def get_data(self):
        raise NotImplementedError
