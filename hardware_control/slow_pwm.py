import time
from threading import Thread

from gpiozero import OutputDevice
from gpiozero.pins.pigpio import PiGPIOFactory


class SlowPWM(Thread):
    factory = PiGPIOFactory()
    pins_in_use = {}

    def __init__(self, pins: list, frequency: float = 1, duty_cycle: float = 0.5):
        """
        This class is meant to do PWM at very low frequencies of 2 pins simultaneously

        :param pins: List of GPIO pin-numbers to control
        :param frequency: Frequency in Hz (<100)
        :param duty_cycle: Duty cycle (0 - 1)
        """
        super().__init__()

        if not 0 <= duty_cycle <= 1:
            raise ValueError("Duty cycle has to be between 0 and 1")

        if frequency > 100:
            raise ValueError("Frequency has to be less than 100Hz")

        self.duty_cycle = duty_cycle
        self.frequency = frequency
        self.on = True
        self.daemon = True  # TODO: is this needed?

        self.pins = []

        for pin_number in pins:
            if pin_number not in self.pins_in_use:
                pin_device = OutputDevice(pin_number,
                                          pin_factory=SlowPWM.factory,
                                          active_high=True,
                                          initial_value=False)
                self.pins_in_use[pin_number] = pin_device
            else:
                pin_device = self.pins_in_use[pin_number]

            self.pins.append(pin_device)

    def stop(self):
        """
        This stops the slow PWM control and sets the pin output to off.
        """
        self.on = False

        for pin in self.pins:
            pin.off()

    def kill(self):
        """
        This stops the output and kills the connection to the underlying pigpio service.
        This will render the object unusable.
        """
        self.stop()
        self.join()
        for pin in self.pins:
            pin.close()

    def run(self) -> None:
        """
        SlowPWM is implemented as a thread and this is the function that gets called when
        the thread gets started.
        """
        period = int((1 / self.frequency) * 1000000000)  # period in nanoseconds
        on_time = int(period * self.duty_cycle)  # duty_cycle in nanoseconds

        turned_off = False

        start = time.time_ns()
        if self.duty_cycle > 0:
            for pin in self.pins:
                pin.on()
        else:
            turned_off = True

        try:
            while self.on:
                time_lapsed_since_start = time.time_ns() - start

                if not 0 <= self.duty_cycle <= 1:
                    raise ValueError("Duty cycle was set incorrectly. "
                                     "It has to be between 0 and 1, not " + str(self.duty_cycle))

                if self.duty_cycle != 1 and not turned_off and time_lapsed_since_start >= on_time:
                    for pin in self.pins:
                        pin.off()
                    turned_off = True

                if self.duty_cycle != 0 and turned_off and time_lapsed_since_start >= period:
                    start = time.time_ns()
                    for pin in self.pins:
                        pin.on()
                    turned_off = False

        finally:
            self.stop()
