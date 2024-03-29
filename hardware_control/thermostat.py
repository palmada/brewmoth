import json
import time
import traceback
from datetime import datetime
from json.decoder import JSONDecodeError
from multiprocessing import Process

# noinspection PyUnresolvedReferences
from systemd import journal

from hardware_control.fan_control import set_fan_speed
from hardware_control.peltier_control import SoftwarePeltierDirectControl
from hardware_control.temperature_sensors import read_temp, check_sensor_types_are_present, \
    get_location_for_sensor
from utilities.constants import *
from utilities.time_temp_parser import get_temp_for_time, parse_json_temps


def read_settings_file():
    attempts = 20
    while attempts > 0:
        try:
            with open(SET_POINT_FILE, 'a+') as set_point_file:
                set_point_file.seek(0)
                if set_point_file:
                    settings_string = set_point_file.read()
                    if len(settings_string) < 1:
                        continue
                    return json.loads(settings_string)
        except (JSONDecodeError, TypeError):
            raise TypeError("File contents not parseable to JSON")
        finally:
            attempts -= 1
    raise IOError("Could not read settings file")


def write_to_settings_file(settings):
    attempts = 20
    while attempts > 0:
        try:
            # Trick to check the file is not open elsewhere
            with open(SET_POINT_FILE, 'w+') as set_point_file:
                set_point_file.seek(0)
                set_point_file.write(json.dumps(settings, indent=2))
                set_point_file.truncate()
                return
        finally:
            attempts -= 1

    raise IOError("Could not write to settings file")


class Thermostat:

    def __init__(self, config: dict):
        with open(SET_POINT_FILE, 'r') as set_point_file:
            settings = json.load(set_point_file)

        if CFG_FAN_SPEED not in config:
            config[CFG_FAN_SPEED] = 0.4

        self.config = config
        self.fan_speed = config[CFG_FAN_SPEED]

        check_sensor_types_are_present(config, SENSOR_TYPE_MAIN)

        self.temp_file = get_location_for_sensor(config, SENSOR_TYPE_MAIN)

        # Read temperature profile from file and get target for current date/time
        self.target_temp = get_temp_for_time(parse_json_temps(settings), datetime.now())  # Celsius

        self.heating_threshold = self.target_temp - settings[SP_HEAT_TOLERANCE]  # Celsius
        self.cooling_threshold = self.target_temp + settings[SP_COOL_TOLERANCE]  # Celsius
        self.sampling = settings[SP_SAMPLING]  # Seconds
        self.alive = True
        self.on = False
        self.peltier_control = SoftwarePeltierDirectControl()
        self.set_state(False)  # Always best to ensure we start with everything off
        self.previous_state = SoftwarePeltierDirectControl.State.OFF

    def __enter__(self):
        journal.write("Thermostat thread starting")
        self.process = Process(target=self.run)
        self.process.daemon = True
        self.process.start()

    def __exit__(self, e_t, e_v, trc):
        self.kill()

    def set_state(self, on: bool):
        """
        Sets on field and sets fan state accordingly

        :param on: Whether the thermostat should control the temperature
        """
        self.on = on
        if not on:
            self.peltier_control.set_state(SoftwarePeltierDirectControl.State.OFF)
            self.previous_state = SoftwarePeltierDirectControl.State.OFF
            set_fan_speed(0)
            journal.write("Thermostat control turned off")
        else:
            journal.write("Thermostat control turned on")
            set_fan_speed(self.fan_speed)

    def kill(self):
        journal.write("Thermostat will get killed")
        self.set_state(False)
        self.alive = False
        self.peltier_control.set_state(SoftwarePeltierDirectControl.State.OFF)
        journal.write("Thermostat finished kill process")

    def run(self) -> None:
        try:
            journal.write("Initialized thermostat with " +
                          str(self.target_temp) + "C set-point, " +
                          str(self.cooling_threshold) + "C cooling threshold, and " +
                          str(self.heating_threshold) + "C heating threshold, and " +
                          str(self.sampling) + " seconds sampling")

            next_read = time.time()
            while self.alive:
                current_time = time.time()

                if current_time > next_read:
                    settings = read_settings_file()
                    read_state = settings[SP_STATE] == ON

                    if read_state != self.on:
                        self.set_state(read_state)

                    if self.on:
                        # Read temperature profile from file and get target for current date/time

                        temp_set_point = get_temp_for_time(parse_json_temps(settings), datetime.now())
                        if temp_set_point != self.target_temp:
                            journal.write("Changed temperature set point to " + str(temp_set_point))
                            self.target_temp = temp_set_point

                        self.heating_threshold = self.target_temp - settings[SP_HEAT_TOLERANCE]
                        self.cooling_threshold = self.target_temp + settings[SP_COOL_TOLERANCE]
                        self.sampling = settings[SP_SAMPLING]

                        current_temp = read_temp(self.temp_file)

                        if not self.heating_threshold <= current_temp <= self.cooling_threshold:
                            if current_temp > self.target_temp:
                                state = SoftwarePeltierDirectControl.State.COOL
                            elif current_temp < self.target_temp:
                                state = SoftwarePeltierDirectControl.State.HEAT
                            else:
                                state = SoftwarePeltierDirectControl.State.OFF
                        else:
                            state = SoftwarePeltierDirectControl.State.OFF

                        if self.previous_state != state:
                            self.peltier_control.set_state(state)
                            self.previous_state = state
                            journal.write("Set peltier state to " + str(state))
                        next_read = current_time + self.sampling

                time.sleep(0.5)  # This allows the thread to check for a kill signal

        except BaseException as e:
            journal.write(traceback.format_exc())
            journal.write("Exception occurred:" + str(e))
        finally:
            message = "Thermostat Control loop stopped"
            journal.write(message)
            self.set_state(False)
