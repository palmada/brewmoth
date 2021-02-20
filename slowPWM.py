#!/usr/bin/env python
import argparse
import sys

from hardware_control.pwm import SlowPWM

if __name__ == '__main__':

    parser = argparse.ArgumentParser()

    parser.add_argument('--duty_cycle', '-d', help='Set the PWM duty cycle as floating point number from 0 to 1')
    parser.add_argument('--frequency', '-f', help='Set the PWM frequency in hertz', default=0.3)
    parser.add_argument('--pump_direction', '-p',
                        help='''
                            Set the heat pump direction, either heating or cooling.
                            1 - Cool
                            2 - Heat
                            '''
                        , default=1)

    args = parser.parse_args()

    frequency = float(args.frequency)
    duty_cycle = float(args.duty_cycle)
    direction = int(args.pump_direction)

    if direction is not 1 or not 2:
        raise Exception("Wrong direction term, has to be either 1 or two, not " + args.pump_direction)

    if not 0 <= duty_cycle <= 1:
        raise Exception("Duty cycle has to be a floating point number from 0 and 1.")

    if frequency >= 100:
        raise Exception("Frequency has to be lower than 100 Hz. Use pigpio for faster frequencies.")

    if direction is 1:
        # Pins for cooling
        pin1 = 5
        pin2 = 27
    else:
        # Pins for heating
        pin1 = 22
        pin2 = 25

    pin1 = SlowPWM(pin1, frequency=frequency, duty_cycle=duty_cycle)
    pin2 = SlowPWM(pin2, frequency=frequency, duty_cycle=duty_cycle)

    try:
        pin1.start()
        pin2.start()

        pin1.join()
        pin2.join()
    finally:
        pin1.on = False
        pin2.on = False

        sys.exit(0)
