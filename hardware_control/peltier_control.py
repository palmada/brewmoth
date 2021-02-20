# Pins for cooling
from hardware_control.fan_control import set_fan_speed
from hardware_control.pwm import SlowPWM

# Pins for cooling
cooling_pin_numbers = [5, 27]

# Pins for heating
heating_pin_numbers = [22, 25]


class PeltierControl:

    def __init__(self, frequency):
        self.frequency = frequency

    def stop(self):
        """
        Stops the peltiers.
        """
        try:
            if self.pins is not None:
                self.pins.stop()
        except:
            '''Ignore'''
        finally:
            set_fan_speed(0)
            return

    def start_pwm(self, duty_cycle):
        """
        Starts the pwm control of the peltiers.

        :param duty_cycle: Duty cycle from -1 to 1. 1 will heat, -1 will cool.
        """

        if not -1 <= duty_cycle <= 1:
            raise ValueError("Duty cycle has to be between -1 and 1")

        if duty_cycle is 0:
            self.stop()
            set_fan_speed(0)
            return
        else:
            self.stop()
            set_fan_speed(abs(duty_cycle))

        if duty_cycle > 0:
            self.pins = SlowPWM(heating_pin_numbers, frequency=self.frequency)
        else:
            self.pins = SlowPWM(cooling_pin_numbers, frequency=self.frequency)

        self.pins.duty_cycle = abs(duty_cycle)
        self.pins.start()
