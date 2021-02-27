import os
import time
from pathlib import Path
from typing import TextIO

# noinspection PyUnresolvedReferences
from systemd import journal
from multiprocessing import Process

from hardware_control.fan_control import set_fan_speed
from hardware_control.peltier_control import SoftwarePeltierDirectControl
from hardware_control.temperature_sensors import read_temp, TEMP_FILE, ROOM_TEMP_FILE
from utilities.constants import READS_FOLDER
from utilities.formatters import timestamp


class Thermostat:

    def __init__(self, target: float = 18.0, tolerance: float = 0.1, sampling: int = 5, record=False):
        super().__init__()
        self.target_temp = target  # Celsius
        self.tolerance = tolerance  # Celsius
        self.sampling = sampling  # Seconds
        self.alive = True
        self.record = record
        self.on = False

        process = Process(target=self.run)
        process.daemon = True
        process.start()

    def set_state(self, on: bool):
        self.on = on
        if not on:
            set_fan_speed(0)
        else:
            set_fan_speed(0.4)

    def run(self) -> None:
        peltier_control = SoftwarePeltierDirectControl(control_fans=False)
        previous_state = SoftwarePeltierDirectControl.State.OFF
        set_fan_speed(0)

        if self.record:
            Path(READS_FOLDER).mkdir(parents=True, exist_ok=True)
            file: TextIO = open(os.path.join(READS_FOLDER, timestamp() + ".csv"), "w")
            message = "Started loop at " + timestamp() + "\n"
            file.write(message)
            journal.write(message)

        try:
            next_read = time.time()
            while self.alive:
                if self.on:
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

                            if self.record:
                                room_temp = read_temp(ROOM_TEMP_FILE)
                                read = "{0}, {1}, {2}, {3}".format(timestamp(), current_temp, room_temp,
                                                                   state)
                                print(read)
                                read += '\n'
                                # noinspection PyUnboundLocalVariable
                                file.write(read)

                        next_read = current_time + self.sampling
        finally:
            if self.record:
                message = "Loop stopped at " + timestamp() + "\n"
                file.write(message)
                journal.write(message)
                file.close()
            peltier_control.set_state(SoftwarePeltierDirectControl.State.OFF)
            set_fan_speed(0)
