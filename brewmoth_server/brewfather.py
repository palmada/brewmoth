from datetime import datetime
from threading import Thread
from typing import List

import requests
# noinspection PyUnresolvedReferences
from systemd import journal

from hardware_control.temperature_sensors import *
from utilities.constants import NAME, SENSOR_TYPE_MAIN, SENSOR_TYPE_ROOM
from utilities.time_temp_parser import SetPointType, SetPoint, sort_set_points

url = 'http://log.brewfather.net/stream?id=OniWOwAOjMnLsM'
json = {
    "temp_unit": "C",  # C, F, K
}


class BrewFatherUpdater(Thread):
    keepAlive: bool = True

    def __init__(self, config: dict):
        super().__init__()
        self.setDaemon(True)
        self.config = config

        for sensor in config[CFG_SENSORS]:
            if sensor[TYPE] == SENSOR_TYPE_MAIN:
                self.main_sensor = sensor[NAME]
            if sensor[TYPE] == SENSOR_TYPE_ROOM:
                self.room_sensor = sensor[NAME]

        if not hasattr(self, 'main_sensor'):
            raise Exception("BrewFatherUpdater could not find the main temperature sensor information")

        json["name"] = config[NAME]  # this will be the ID in Brewfather
        journal.write("Did initialize BrewFatherUpdater")

    def run(self) -> None:

        try:
            while self.keepAlive:
                try:
                    temperatures = read_temps(self.config)

                    # We find now the main and room sensor, if present
                    for temperature in temperatures:
                        if temperature == self.main_sensor:
                            json["temp"] = temperatures[temperature]
                        if hasattr(self, 'room_sensor') and temperature == self.room_sensor:
                            json["ext_temp"] = temperatures[temperature]

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
