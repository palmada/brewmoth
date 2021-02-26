#!/usr/bin/env python
import argparse
import sys

from hardware_control.peltier_control import SoftwarePeltierPWMControl
from hardware_control.slow_pwm import SlowPWM

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('--duty_cycle', '-d', help='Set the PWM duty cycle as floating point number from 0 to 1')
    parser.add_argument('--frequency', '-f', help='Set the PWM frequency in hertz', default=0.3)
    parser.add_argument('--pump_direction', '-p',
                        help='''Set the heat pump direction, either heating or cooling.
                            -1 - Cool
                            1 - Heat''', default=-1)

    args = parser.parse_args()

    frequency = float(args.frequency)
    duty_cycle = float(args.duty_cycle)
    direction = int(args.pump_direction)

    if direction is not -1 and not 1:
        raise Exception("Wrong direction term, has to be either 1 or -1, not: " + args.pump_direction)

    if not 0 <= duty_cycle <= 1:
        raise Exception("Duty cycle has to be a floating point number from 0 and 1.")

    if frequency >= 100:
        raise Exception("Frequency has to be lower than 100 Hz. Use pigpio for faster frequencies.")

    print("Will perform pwm test at", frequency, "Hz with a duty cycle of", duty_cycle)

    if direction is -1:
        # Pins for cooling
        print("Will cool.")
        pins = SoftwarePeltierPWMControl.cooling_pin_numbers
    else:
        print("Will heat")
        # Pins for heating
        pins = SoftwarePeltierPWMControl.heating_pin_numbers

    pin_control_thread = SlowPWM(pins, frequency=frequency, duty_cycle=duty_cycle)

    try:
        pin_control_thread.start()

        pin_control_thread.join()
    except KeyboardInterrupt:
        print("\nExiting.")
    finally:
        pin_control_thread.kill()
        sys.exit(0)
