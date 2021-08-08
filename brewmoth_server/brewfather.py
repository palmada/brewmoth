from datetime import datetime
from threading import Thread
from typing import List

import requests

from hardware_control.temperature_sensors import *
from utilities.time_temp_parser import SetPointType, SetPoint, sort_set_points

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


def brewfather_data_import(received_json: dict) -> List[SetPoint]:
    temps = received_json["recipe"]["fermentation"]["steps"]

    batch_notes = received_json["notes"]
    note_time_stamps = []

    for note in batch_notes:
        if note["status"] == "Fermenting":
            note_time_stamps.append(note["timestamp"])

    if note_time_stamps:
        note_time_stamps = sorted(note_time_stamps)

        brew_time = datetime.fromtimestamp(note_time_stamps[0] / 1000).time()
    else:
        brew_time = None

    set_points = []

    for temp in temps:
        target_temp = temp["stepTemp"]
        step_date = datetime.fromtimestamp(temp["actualTime"] / 1000)
        step_type = temp["type"]

        if step_type == "Conditioning":
            continue

        if brew_time is not None:
            step_date = step_date.replace(hour=brew_time.hour, minute=brew_time.minute)

        if temp["ramp"] is not None:
            set_point_type = SetPointType.RAMP
        else:
            set_point_type = SetPointType.CRASH

        set_point = SetPoint(target_temp, step_date, set_point_type)
        set_points.append(set_point)

    return sort_set_points(set_points)
