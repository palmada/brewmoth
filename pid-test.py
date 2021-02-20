import argparse
import os

from simple_pid import PID

from hardware_control.peltier_control import PeltierControl
from hardware_control.temperature_sensors import temp_file, read_temp
from utilities.formatters import timestamp

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('--temperature', '-t', help='Target temperature', default=15)

    args = parser.parse_args()
    target_temp = float(args.temperature)

    os.system('modprobe w1-gpio')
    os.system('modprobe w1-therm')

    pid = PID(1, 0.1, 0.05, setpoint=target_temp)

    # Update every
    pid.sample_time = 30  # seconds

    # Set the maximum range of peltier control
    pid.output_limits = (-1, 1)

    # Assuming temperature control is an  integrating process, this helps prevent overshoot
    pid.proportional_on_measurement = True

    peltiers = PeltierControl(frequency=5)

    current_value = 0
    try:
        while True:
            current_temp = read_temp(temp_file)
            peltier_duty_cycle = pid(current_temp)

            if peltier_duty_cycle != current_value:
                print(timestamp(), peltier_duty_cycle, pid.components)
                peltiers.start_pwm(peltier_duty_cycle)
                current_value = peltier_duty_cycle
    except KeyboardInterrupt:
        print("Exiting.")
    finally:
        peltiers.stop()
