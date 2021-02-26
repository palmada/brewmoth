#!/usr/bin/env python
import argparse
import os
from pathlib import Path

from simple_pid import PID

from hardware_control.peltier_control import SoftwarePeltierPWMControl
from hardware_control.slow_pwm import SlowPWM
from hardware_control.temperature_sensors import temp_file, read_temp, room_temp_file
from utilities.constants import READS_FOLDER
from utilities.formatters import timestamp

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('--temperature', '-t', help='Target temperature', default=15)

    args = parser.parse_args()
    target_temp = float(args.temperature)

    os.system('modprobe w1-gpio')
    os.system('modprobe w1-therm')

    # pid = PID(0.7, 130, 70, setpoint=target_temp) 21:38 on feb 23
    # pid = PID(0.6, 0.005, 40, setpoint=target_temp)
    # pid = PID(4.154, 0.0155, 276, setpoint=target_temp) # 22:23 on feb 24 untested
    pid = PID(1.65, 0.00407, 145.2, setpoint=target_temp) # 22:23 on feb 24 tested alternative

    # Update every
    pid.sample_time = 30  # seconds

    # Set the maximum range of peltier control
    pid.output_limits = (-1, 0)  # (-1, 0) means cooling only since there is something wrong when heating

    # Assuming temperature control is an  integrating process, this helps prevent overshoot
    pid.proportional_on_measurement = True

    peltiers = SoftwarePeltierPWMControl(frequency=0.2)

    current_value = 0

    print("Target temp:", pid.setpoint)
    print("Timestamp, Temperature, Room Temperature, PID output, Kp, Ki, Kd")

    Path(READS_FOLDER).mkdir(parents=True, exist_ok=True)

    file = open(os.path.join(READS_FOLDER, timestamp() + ".pid.csv"), "w")

    try:
        while True:
            current_temp = read_temp(temp_file)
            room_temp = read_temp(room_temp_file)
            peltier_duty_cycle = pid(current_temp)

            if peltier_duty_cycle != current_value:
                peltiers.set_pwm(peltier_duty_cycle)
                current_value = peltier_duty_cycle

                read = "{0}, {1}, {2}, {3}, {4}, {5}, {6}".format(timestamp(), current_temp, room_temp,
                                                                  peltier_duty_cycle, *pid.components)
                print(read)
                read += '\n'
                file.write(read)

    except KeyboardInterrupt:
        print("\nTest stopped.")
    finally:
        peltiers.kill()
        file.close()
