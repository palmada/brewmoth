# Pins for cooling
import os
from enum import Enum

import pigpio

from hardware_control.fan_control import set_fan_speed
from hardware_control.slow_pwm import SlowPWM

pin_control = pigpio.pi()


class SoftwarePeltierDirectControl:
    # Pins for cooling
    heating_pin_numbers = [5, 27]

    # Pins for heating
    cooling_pin_numbers = [22, 25]

    class State(Enum):
        HEAT = 1
        COOL = -1
        OFF = 0

    def __init__(self, control_fans: bool):
        self.set_fans = control_fans

    def stop(self):
        """
        Turns off peltiers.
        """
        for pin in self.cooling_pin_numbers:
            pin_control.write(pin, 0)

        for pin in self.heating_pin_numbers:
            pin_control.write(pin, 0)

        if self.set_fans:
            set_fan_speed(0)

    def set_state(self, state: State):
        """
        Starts, stops or modifies the pwm control of the peltiers.

        :param state: Set state to heat, cool or off
        """

        if state is self.State.OFF:
            self.stop()
        else:
            if self.set_fans:
                set_fan_speed(0.4)

            if state is self.State.HEAT:
                for pin in self.cooling_pin_numbers:
                    pin_control.write(pin, 0)

                for pin in self.heating_pin_numbers:
                    pin_control.write(pin, 1)
            else:
                for pin in self.cooling_pin_numbers:
                    pin_control.write(pin, 1)

                for pin in self.heating_pin_numbers:
                    pin_control.write(pin, 0)


class SoftwarePeltierPWMControl:
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
            set_fan_speed(0.4)

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

    pin_control.set_PWM_range(SoftwarePeltierPWMControl.cooling_pin_numbers[0], pwm_range)
    pin_control.set_PWM_range(SoftwarePeltierPWMControl.cooling_pin_numbers[1], pwm_range)
    pin_control.set_PWM_range(SoftwarePeltierPWMControl.heating_pin_numbers[0], pwm_range)
    pin_control.set_PWM_range(SoftwarePeltierPWMControl.heating_pin_numbers[1], pwm_range)

    pin_control.set_PWM_frequency(SoftwarePeltierPWMControl.cooling_pin_numbers[0], frequency)
    pin_control.set_PWM_frequency(SoftwarePeltierPWMControl.cooling_pin_numbers[1], frequency)
    pin_control.set_PWM_frequency(SoftwarePeltierPWMControl.heating_pin_numbers[0], frequency)
    pin_control.set_PWM_frequency(SoftwarePeltierPWMControl.heating_pin_numbers[1], frequency)

    if power == 0:
        pin_control.set_PWM_dutycycle(SoftwarePeltierPWMControl.cooling_pin_numbers[0], 0)
        pin_control.set_PWM_dutycycle(SoftwarePeltierPWMControl.cooling_pin_numbers[1], 0)
        pin_control.set_PWM_dutycycle(SoftwarePeltierPWMControl.heating_pin_numbers[0], 0)
        pin_control.set_PWM_dutycycle(SoftwarePeltierPWMControl.heating_pin_numbers[1], 0)

    elif heat:
        # It's important to first turn off the other gates
        pin_control.set_PWM_dutycycle(SoftwarePeltierPWMControl.cooling_pin_numbers[0], 0)
        pin_control.set_PWM_dutycycle(SoftwarePeltierPWMControl.cooling_pin_numbers[1], 0)

        pin_control.set_PWM_dutycycle(SoftwarePeltierPWMControl.heating_pin_numbers[0], power)
        pin_control.set_PWM_dutycycle(SoftwarePeltierPWMControl.heating_pin_numbers[1], power)
    else:  # Will cool
        pin_control.set_PWM_dutycycle(SoftwarePeltierPWMControl.heating_pin_numbers[0], 0)
        pin_control.set_PWM_dutycycle(SoftwarePeltierPWMControl.heating_pin_numbers[1], 0)

        pin_control.set_PWM_dutycycle(SoftwarePeltierPWMControl.cooling_pin_numbers[0], power)
        pin_control.set_PWM_dutycycle(SoftwarePeltierPWMControl.cooling_pin_numbers[1], power)
