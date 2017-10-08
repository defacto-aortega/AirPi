import mcp3008
import sensor


class Analogue(sensor.Sensor):
    requiredOptions = ["adcPin", "measurement", "sensorName"]
    optionalOptions = ["pullUpResistance", "pullDownResistance"]

    def __init__(self, data):

        self.adc = mcp3008.MCP3008.sharedClass

        self.adcPin = int(data["adcPin"])
        self.valName = data["measurement"]
        self.sensorName = data["sensorName"]
        self.pullUp, self.pullDown = None, None
        self.valUnit = "Ohms"
        self.valSymbol = "Ohms"

        if "pullUpResistance" in data:
            self.pullUp = int(data["pullUpResistance"])

        if "pullDownResistance" in data:
            self.pullDown = int(data["pullDownResistance"])

        if self.pullUp is not None and self.pullDown is not None:
            print "Please choose whether there is a pull up or pull down resistor for the " + self.valName + " measurement by only entering one of them into the settings file "
            raise ConfigError

        if self.pullUp is None and self.pullDown is None:
            self.valUnit = "millvolts"
            self.valSymbol = "mV"

    def getVal(self):

        # Get result from adc
        result = self.adc.readADC(self.adcPin)

        if result == 0:
            print "Check wiring for the " + self.sensorName + " measurement, no voltage detected on ADC input " + str(self.adcPin)
            return None
        if result == 1023:
            print "Check wiring for the " + self.sensorName + " measurement, full voltage detected on ADC input " + str(self.adcPin)
            return None

        if self.pullDown is not None:
            return self.getPullDown(result)
        elif self.pullUp is not None:
            return self.getPullUp(result)
        else:
            return self.getResult(result)

    def getPullDown(self, result):
        vin = 3.3
        vout = float(result) / 1023 * vin
        return (self.pullDown * vin) / vout - self.pullDown

    def getPullUp(self, result):
        vin = 3.3
        vout = float(result) / 1023 * vin
        return self.pullUp / ((vin / vout) - 1)

    def getResult(self, result):
        vin = 3.3
        vout = float(result) / 1023 * vin
        return vout * 1000

    def get_data(self):
        pass


class ConfigError(Exception):
    pass
