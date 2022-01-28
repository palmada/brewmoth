import time
from threading import Thread
from typing import List

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
            while self.keepAlive:
                try:
                    temperatures = read_temps(self.config)

                    for logger in self.loggers:
                        logger.log(temperatures)

                    time.sleep(self.delay_ms)
                except Exception as e:
                    print("Error:", str(e))

        except Exception as e:
            print("Error:", str(e))