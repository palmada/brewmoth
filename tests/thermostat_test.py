#!/usr/bin/env python
import argparse
import json
import os
import time
from pathlib import Path

from hardware_control.fan_control import set_fan_speed
from hardware_control.peltier_control import SoftwarePeltierDirectControl
from hardware_control.temperature_sensors import read_temp, sensor_location, check_sensors_are_present
from utilities.constants import READS_FOLDER, CONFIG_FILE, SENSOR_TEMP, SENSOR_ROOM, CFG_SENSORS
from utilities.formatters import timestamp

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('--temperature', '-t', help='Target temperature', default=15)
    parser.add_argument('--tolerance', '-to', help='Allowed temperature deviation', default=0.10)
    parser.add_argument('--sampling', '-s', help='How often to sample', default=5)

    args = parser.parse_args()
    target_temp = float(args.temperature)
    sampling = float(args.sampling)
    tolerance = float(args.tolerance)

    os.system('modprobe w1-gpio')
    os.system('modprobe w1-therm')

    current_value = 0

    print("Target temp:", target_temp)
    print("Timestamp, Temperature, Room Temperature, Peltier state")

    Path(READS_FOLDER).mkdir(parents=True, exist_ok=True)

    file = open(os.path.join(READS_FOLDER, timestamp() + ".pid.csv"), "w")

    peltier_control = SoftwarePeltierDirectControl(False)
    previous_state = SoftwarePeltierDirectControl.State.OFF

    set_fan_speed(0.4)

    with open(CONFIG_FILE, 'r') as config_file:
        config_data = json.loads(config_file.read())

    check_sensors_are_present(config_data, SENSOR_TEMP, SENSOR_ROOM)

    temp_file = sensor_location(config_data[CFG_SENSORS][SENSOR_TEMP])
    room_temp_file = sensor_location(config_data[CFG_SENSORS][SENSOR_ROOM])

    try:
        next_read = time.time()
        while True:
            current_time = time.time()

            if current_time > next_read:
                current_temp = read_temp(temp_file)
                room_temp = read_temp(room_temp_file)

                if not target_temp - tolerance <= current_temp <= target_temp + tolerance:
                    if current_temp > target_temp:
                        state = SoftwarePeltierDirectControl.State.COOL
                    else:
                        state = SoftwarePeltierDirectControl.State.OFF  # TODO: change to heat once fixed
                else:
                    state = SoftwarePeltierDirectControl.State.OFF

                if previous_state != state:
                    peltier_control.set_state(state)

                    read = "{0}, {1}, {2}, {3}".format(timestamp(), current_temp, room_temp,
                                                       state)
                    print(read)
                    read += '\n'
                    file.write(read)
                    previous_state = state

                next_read = current_time + sampling

    except KeyboardInterrupt:
        print("\nTest stopped.")
    finally:
        peltier_control.set_state(SoftwarePeltierDirectControl.State.OFF)
        set_fan_speed(0)
        file.close()
