#!/usr/bin/python

import sensor


class DS18S20(sensor.Sensor):
    requiredOptions = ["pinNumber"]
    optionalOptions = ["unit"]

    def __init__(self, data):
        self.sensorName = "DS18S20"
        self.pinNum = int(data["pinNumber"])
        self.valUnit = "Celsius"
        self.valSymbol = "C"
        self.valName = "Temperature"

        # Case unit was set, and is Fahrenheit
        if "unit" in data:
            if data["unit"] == "F":
                self.valUnit = "Fahrenheit"
                self.valSymbol = "F"

    def getVal(self):
        file = open('/sys/devices/w1_bus_master1/w1_master_slaves')
        w1_slaves = file.readlines()
        file.close()

        # Fuer jeden 1-Wire Slave aktuelle Temperatur ausgeben
        for line in w1_slaves:
            # 1-wire Slave extrahieren
            w1_slave = line.split("\n")[0]
            # 1-wire Slave Datei lesen
            file = open('/sys/bus/w1/devices/' + str(w1_slave) + '/w1_slave')
            file_content = file.read()
            file.close()

            # Read
            string_value = file_content.split("\n")[1].split(" ")[9]
            temperature = float(string_value[2:]) / 1000

            if temperature > 0:
                return temperature

        return None

    def get_data(self):
        pass
