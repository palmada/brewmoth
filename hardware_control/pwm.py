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
                if self.duty_cycle != 1 and not turned_off and lapsed_time >= on_time:
                    self.pin.off()
                    turned_off = True

                if lapsed_time >= period:
                    start = time.time_ns()
                    self.pin.on()
                    turned_off = False
        finally:
            self.pin.off()
