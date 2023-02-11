import time
from threading import Thread
from typing import List

# noinspection PyUnresolvedReferences
from systemd import journal
from hardware_control.temperature_sensors import read_temps
from utilities.constants import CFG_WRITE_TO_DISK, NAME
from utilities.file_handling import create_time_stamped_csv
from utilities.formatters import timestamp


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
        self.write_to_disk = CFG_WRITE_TO_DISK in config
        if self.write_to_disk:
            journal.write("Will write data to disk")
            self.csv = create_time_stamped_csv()
            journal.write("Created file " + self.csv.name)

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

                        if self.write_to_disk:
                            read = timestamp() + "," + self.config[NAME]

                            for temperature in temperatures:
                                read += "," + str(temperatures[temperature])

                            read += "\n"
                            self.csv.write(read)
                            # `File` is buffered and therefore won't write straight to disk.
                            # For debugging and making sure we don't miss any reads,
                            # we force writer to write right-away with flush
                            self.csv.flush()

                        next_read = current_time + self.delay_ms
                    except Exception as e:
                        print("Error:", str(e))

                time.sleep(0.5)  # This allows the thread to check for a kill signal

            journal.write("Logging thread finished")

        except Exception as e:
            print("Error:", str(e))
        finally:
            if self.write_to_disk:
                self.csv.close()