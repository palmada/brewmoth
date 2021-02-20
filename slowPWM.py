#!/usr/bin/env python
import argparse
import sys
import time
from threading import Thread

from gpiozero import DigitalOutputDevice
from gpiozero.pins.pigpio import PiGPIOFactory


class SlowPWM(Thread):
    factory = PiGPIOFactory()

    def __init__(self, pin: int, frequency: float = 1, duty_cycle: float = 0.5):
        """
        This class is meant to do PWM at very low frequencies

        :param pin: GPIO pin number
        :param frequency: Frequency in Hz (<100)
        :param duty_cycle: Duty cycle (0 - 1)
        """
        super().__init__()

        assert 0 <= duty_cycle <= 1
        assert frequency < 100

        self.duty_cycle = duty_cycle
        self.frequency = frequency
        self.on = True
        self.daemon = True
        self.number = pin
        self.pin = DigitalOutputDevice(pin, pin_factory=SlowPWM.factory)

    def run(self) -> None:
        period = int((1 / self.frequency) * 1000000000)  # period in nanoseconds
        on_time = int(period * self.duty_cycle)  # duty_cycle in nanoseconds

        start = time.time_ns()
        self.pin.on()

        turned_off = False

        try:
            while self.on:
                lapsed_time = time.time_ns() - start
                if duty_cycle != 1 and not turned_off and lapsed_time >= on_time:
                    self.pin.off()
                    turned_off = True

                if lapsed_time >= period:
                    start = time.time_ns()
                    self.pin.on()
                    turned_off = False
        finally:
            self.pin.off()


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
