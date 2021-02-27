import time
from threading import Thread

from hardware_control.fan_control import set_fan_speed
from hardware_control.peltier_control import SoftwarePeltierDirectControl
from hardware_control.temperature_sensors import read_temp, TEMP_FILE


class Thermostat(Thread):

    def __init__(self, target: float = 18.0, tolerance: float = 0.1, sampling: int = 5):
        super().__init__()
        self.target_temp = target  # Celsius
        self.tolerance = tolerance  # Celsius
        self.sampling = sampling  # Seconds
        self.alive = True

    def run(self) -> None:
        peltier_control = SoftwarePeltierDirectControl(control_fans=False)
        previous_state = SoftwarePeltierDirectControl.State.OFF

        set_fan_speed(0.4)

        try:
            next_read = time.time()
            while self.alive:
                current_time = time.time()

                if current_time > next_read:
                    current_temp = read_temp(TEMP_FILE)

                    if not self.target_temp - self.tolerance <= current_temp <= self.target_temp + self.tolerance:
                        if current_temp > self.target_temp:
                            state = SoftwarePeltierDirectControl.State.COOL
                        else:
                            state = SoftwarePeltierDirectControl.State.OFF  # TODO: change to heat once fixed
                    else:
                        state = SoftwarePeltierDirectControl.State.OFF

                    if previous_state != state:
                        peltier_control.set_state(state)
                        previous_state = state

                    next_read = current_time + self.sampling
        finally:
            peltier_control.set_state(SoftwarePeltierDirectControl.State.OFF)
            set_fan_speed(0)
