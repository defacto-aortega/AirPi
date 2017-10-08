class AirPiException(Exception):

    def __init__(self, message):
        self.message = message
        print self.message
        pass
