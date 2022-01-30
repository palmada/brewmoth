import time
from threading import Thread
from typing import List

# noinspection PyUnresolvedReferences
from systemd import journal
from hardware_control.temperature_sensors import read_temps


class Logger:

    def log(self, temperatures: dict):
        pass


class UpdateThread(Thread):
    keepAlive: bool = True

    def __init__(self, config: dict, loggers: List[Logger], delay_ms: int = 900):
        super().__init__()
        self.delay_ms = delay_ms
        self.loggers = loggers
        self.setDaemon(True)
        self.config = config

    def run(self) -> None:

        try:
            next_read = time.time()
            while self.keepAlive:
                current_time = time.time()
                if current_time > next_read:
                    try:
                        temperatures = read_temps(self.config)

                        for logger in self.loggers:
                            logger.log(temperatures)

                        next_read = current_time + self.delay_ms
                    except Exception as e:
                        print("Error:", str(e))

                time.sleep(0.5)  # This allows the thread to check for a kill signal

            journal.write("Logging thread finished")

        except Exception as e:
            print("Error:", str(e))