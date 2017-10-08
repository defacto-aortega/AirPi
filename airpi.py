# This file takes in inputs from a variety of sensor files, and outputs information to a variety of services
import sys
import RPi.GPIO as GPIO
import ConfigParser
import time
import inspect
import os

from helpers import exceptions
from sensors import sensor
from outputs import output

sys.dont_write_bytecode = True


def get_subclasses(mod, cls):
    for name, obj in inspect.getmembers(mod):
        if hasattr(obj, "__bases__") and cls in obj.__bases__:
            return obj


class AirPi:
    CONST_SENSORSCFG = "sensors.cfg"
    CONST_OUTPUTSCFG = "outputs.cfg"
    CONST_SETTINGSCFG = "settings.cfg"

    def __init__(self):
        if not os.path.isfile(self.CONST_SENSORSCFG):
            raise exceptions.AirPiException("Unable to access config file: sensors.cfg")

        if not os.path.isfile(self.CONST_OUTPUTSCFG):
            raise exceptions.AirPiException("Unable to access config file: outputs.cfg")

        if not os.path.isfile(self.CONST_SETTINGSCFG):
            raise exceptions.AirPiException("Unable to access config file: settings.cfg")

    def load_from_configuration(self, configuration_name):
        config = ConfigParser.SafeConfigParser()
        config.read(configuration_name)
        sections = config.sections()

        print "Configurations found for " + configuration_name

        # We need to set the module
        module_dir = "sensors"
        if configuration_name == self.CONST_OUTPUTSCFG:
            module_dir = "outputs"

        inst_array = []
        for section in sections:
            print section
            try:
                enabled = True
                if config.has_option(section, "enabled"):
                    enabled = config.getboolean(section, "enabled")

                async = False
                if config.has_option(section, "async"):
                    async = config.getboolean(section, "async")

                if enabled:
                    if not config.has_option(section, "filename"):
                        raise exceptions.AirPiException("No filename config option found for " + module_dir +
                                                        " plugin " + section)

                    file_name = config.get(section, "filename")
                    mod = __import__(module_dir + '.' + file_name, fromlist=['a'])

                    # Load subclasses
                    sub_class = None
                    if module_dir == "sensors":
                        sub_class = get_subclasses(mod, sensor.Sensor)

                    if module_dir == "outputs":
                        sub_class = get_subclasses(mod, output.Output)

                    if sub_class is None:
                        raise exceptions.AirPiException("Could not find a subclass for " + module_dir + " in module"
                                                        + file_name)
                    reqd = sub_class.requiredOptions
                    opt = sub_class.optionalOptions
                    plugin_data = {}

                    # Get required configurations
                    for required_field in reqd:
                        if config.has_option(section, required_field):
                            plugin_data[required_field] = config.get(section, required_field)
                        else:
                            raise exceptions.AirPiException(
                                "Missing required field '" + required_field + "' for sensor plugin " + section)

                    # Get optional configurations
                    for optional in opt:
                        if config.has_option(section, optional):
                            plugin_data[optional] = config.get(section, optional)

                    # Create an instance of that sensor
                    inst_class = sub_class(plugin_data)
                    inst_class.async = async

                    # Append that instance for processing
                    inst_array.append(inst_class)

                    print ("Success: Loaded "+module_dir+" plugin " + section)

            except exceptions.AirPiException as ae:
                raise ae
            except Exception as e:
                print e
                raise exceptions.AirPiException("Did not import "+module_dir+" plugin: " + section)

        return inst_array

    def main(self):
        # Read main configurations
        main_config = ConfigParser.SafeConfigParser()
        main_config.read(self.CONST_SETTINGSCFG)
        delay_time = main_config.getfloat("Main", "uploadDelay")
        red_pin = main_config.getint("Main", "redPin")
        green_pin = main_config.getint("Main", "greenPin")

        # Set GPIO settings
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)  # Use BCM GPIO numbers.
        GPIO.setup(red_pin, GPIO.OUT, initial=GPIO.LOW)
        GPIO.setup(green_pin, GPIO.OUT, initial=GPIO.LOW)

        # Load plugins
        sensor_plugins = self.load_from_configuration(self.CONST_SENSORSCFG)
        output_plugins = self.load_from_configuration(self.CONST_OUTPUTSCFG)

        last_updated = 0

        while True:
            current_time = time.time()
            if (current_time - last_updated) > delay_time:
                last_updated = current_time
                data = []

                # Collect the data from each sensor
                for i in sensor_plugins:
                    data_dict = {}
                    val = i.getVal()
                    if val is None:  # this means it has no data to upload.
                        continue
                    data_dict["value"] = i.getVal()
                    data_dict["unit"] = i.valUnit
                    data_dict["symbol"] = i.valSymbol
                    data_dict["name"] = i.valName
                    data_dict["sensor"] = i.sensorName
                    data.append(data_dict)
                working = True

                for i in output_plugins:
                    working = working and i.output_data(data)

                if working:
                    print "Uploaded successfully"
                    GPIO.output(green_pin, GPIO.HIGH)
                else:
                    print "Failed to upload"
                    GPIO.output(red_pin, GPIO.HIGH)

                time.sleep(1)
                GPIO.output(green_pin, GPIO.LOW)
                GPIO.output(red_pin, GPIO.LOW)


if __name__ == "__main__":
    AirPi().main()
