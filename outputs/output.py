class Output:
    requiredOptions = []
    optionalOptions = []

    def __init__(self, data):
        raise NotImplementedError

    def output_data(self, data_points):
        raise NotImplementedError
