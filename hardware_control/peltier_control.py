# Pins for cooling
import os

import pigpio

from hardware_control.fan_control import set_fan_speed
from hardware_control.slow_pwm import SlowPWM


class SoftwarePeltierControl:
    # Pins for cooling
    cooling_pin_numbers = [5, 27]

    # Pins for heating
    heating_pin_numbers = [22, 25]

    def __init__(self, frequency):
        self.frequency = frequency

        self.cooling_pins_control = SlowPWM(self.cooling_pin_numbers,
                                            frequency=self.frequency,
                                            duty_cycle=0)
        self.heating_pins_control = SlowPWM(self.heating_pin_numbers,
                                            frequency=self.frequency,
                                            duty_cycle=0)

        self.cooling_pins_control.start()
        self.heating_pins_control.start()

    def stop(self):
        """
        Turns off peltiers.
        """
        self.cooling_pins_control.duty_cycle = 0
        self.heating_pins_control.duty_cycle = 0
        set_fan_speed(0)

    def kill(self):
        """
        Kills threads for both heating and cooling.
        Once kill has been called, the object will no longer be usable.
        """
        self.stop()
        self.cooling_pins_control.kill()
        self.heating_pins_control.kill()

    def set_pwm(self, duty_cycle):
        """
        Starts, stops or modifies the pwm control of the peltiers.

        :param duty_cycle: Duty cycle from -1 to 1. 1 will heat, -1 will cool, 0 will stop the peltiers.
        """

        if not -1 <= duty_cycle <= 1:
            raise ValueError("Duty cycle has to be between -1 and 1")

        heat = duty_cycle > 0
        duty_cycle = abs(duty_cycle)

        if duty_cycle is 0:
            self.stop()
            return
        else:
            set_fan_speed(duty_cycle)

        if heat:
            self.cooling_pins_control.duty_cycle = 0
            self.heating_pins_control.duty_cycle = duty_cycle
        else:
            self.cooling_pins_control.duty_cycle = duty_cycle
            self.heating_pins_control.duty_cycle = 0


# Hardware PWM constants
pwm_range = 40000  # For our 25kHz PWM signal, the period is 40000 nanoseconds
frequency = 10  # Hz


def set_hw_pwm_peltier_control(power):
    heat = power < 0
    power = abs(power)
    if power == 0:
        message = "echo Turning off Peltiers"
    else:
        message = "echo Set Peltier power to "
        if heat:
            message += "heat"
        else:
            message += "cool"
        message += " at " + str(power * 100) + "% power."
    os.system(message)

    power = int(power * pwm_range)

    pins = pigpio.pi()

    pins.set_PWM_range(SoftwarePeltierControl.cooling_pin_numbers[0], pwm_range)
    pins.set_PWM_range(SoftwarePeltierControl.cooling_pin_numbers[1], pwm_range)
    pins.set_PWM_range(SoftwarePeltierControl.heating_pin_numbers[0], pwm_range)
    pins.set_PWM_range(SoftwarePeltierControl.heating_pin_numbers[1], pwm_range)

    pins.set_PWM_frequency(SoftwarePeltierControl.cooling_pin_numbers[0], frequency)
    pins.set_PWM_frequency(SoftwarePeltierControl.cooling_pin_numbers[1], frequency)
    pins.set_PWM_frequency(SoftwarePeltierControl.heating_pin_numbers[0], frequency)
    pins.set_PWM_frequency(SoftwarePeltierControl.heating_pin_numbers[1], frequency)

    if power == 0:
        pins.set_PWM_dutycycle(SoftwarePeltierControl.cooling_pin_numbers[0], 0)
        pins.set_PWM_dutycycle(SoftwarePeltierControl.cooling_pin_numbers[1], 0)
        pins.set_PWM_dutycycle(SoftwarePeltierControl.heating_pin_numbers[0], 0)
        pins.set_PWM_dutycycle(SoftwarePeltierControl.heating_pin_numbers[1], 0)

    elif heat:
        # It's important to first turn off the other gates
        pins.set_PWM_dutycycle(SoftwarePeltierControl.cooling_pin_numbers[0], 0)
        pins.set_PWM_dutycycle(SoftwarePeltierControl.cooling_pin_numbers[1], 0)

        pins.set_PWM_dutycycle(SoftwarePeltierControl.heating_pin_numbers[0], power)
        pins.set_PWM_dutycycle(SoftwarePeltierControl.heating_pin_numbers[1], power)
    else:  # Will cool
        pins.set_PWM_dutycycle(SoftwarePeltierControl.heating_pin_numbers[0], 0)
        pins.set_PWM_dutycycle(SoftwarePeltierControl.heating_pin_numbers[1], 0)

        pins.set_PWM_dutycycle(SoftwarePeltierControl.cooling_pin_numbers[0], power)
        pins.set_PWM_dutycycle(SoftwarePeltierControl.cooling_pin_numbers[1], power)
