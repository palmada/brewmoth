from threading import Thread

import requests

from hardware_control.temperature_sensors import *

url = 'http://log.brewfather.net/stream?id=OniWOwAOjMnLsM'
json = {
    "name": "Moth",  # Required field, this will be the ID in Brewfather
    "temp": -5,
    "temp_unit": "C",  # C, F, K
}


class BrewFatherUpdater(Thread):

    keepAlive: bool = True

    def __init__(self):
        super().__init__()
        self.setDaemon(True)

    def run(self) -> None:

        try:
            while self.keepAlive:
                try:
                    try:
                        room_temp = str(read_temp(ROOM_TEMP_FILE))
                        json["ext_temp"] = room_temp
                    except Exception as e:
                        print("Failed to get room temp:", str(e))

                    try:
                        fermenter_temp = str(read_temp(TEMP_FILE))
                        json["temp"] = fermenter_temp
                    except Exception as e:
                        print("Failed to get fridge temp:", str(e))

                    if "ext_temp" not in json and "temp" not in json:
                        raise Exception("Failed to get either temperature")

                    requests.post(url, data=json)
                    time.sleep(900)
                except Exception as e:
                    print("Error:", str(e))

        except Exception as e:
            print("Error:", str(e))
