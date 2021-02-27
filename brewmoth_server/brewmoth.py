import json
import os

from flask import Flask, request
from flask_cors import CORS

from hardware_control.temperature_sensors import *
from hardware_control.thermostat import Thermostat
from utilities.formatters import timestamp
from utilities.constants import *
from brewmoth_server.brewfather import BrewFatherUpdater

BATCH_FOLDER = MOTH_LOCATION + 'batches'
ALLOWED_EXTENSIONS = {'txt', 'json'}

app = Flask(__name__)
CORS(app)


class Brewmoth:

    def __init__(self):
        if not os.path.exists(BATCH_FOLDER):
            os.makedirs(BATCH_FOLDER)

        self.thermostat: Thermostat


moth = Brewmoth()


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/brewfather", methods=['GET', 'POST'])
def save_post():
    if request.method == 'POST':

        if request.is_json:
            received_json = request.get_json()
            time_stamp = timestamp() + ".batch"
            file = open(os.path.join(BATCH_FOLDER, time_stamp), "w")
            file.write(json.dumps(received_json))
            file.close()
        else:
            return "request was not a json"

        return json.dumps({'success': True}), 200, {'ContentType': 'application/json'}
    return "didn't get a post"


@app.route('/cli', methods=['GET', 'POST'])
def hello():
    try:
        if request.method == 'POST':
            data = request.get_json()

            if CLI_SET_TEMP in data:
                set_point = data[CLI_SET_TEMP]

                if set_point is CLI_OFF and moth.thermostat is not None:
                    moth.thermostat.alive = False
                    moth.thermostat = None
                else:
                    try:
                        set_point = float(set_point)
                    except ValueError:
                        return "Error parsing requested temperature"

                    if moth.thermostat is None:
                        moth.thermostat = Thermostat(target=set_point)
                        moth.thermostat.start()
                    else:
                        moth.thermostat.target_temp = set_point

            elif data == CLI_GET_TEMP:
                return {
                    CLI_FRIDGE: read_temp(TEMP_FILE),
                    CLI_ROOM: read_temp(ROOM_TEMP_FILE)
                }
            else:
                return "Got: " + data

        else:
            return "Not a post"

    except Exception as e:
        return "Exception: " + str(e)


if __name__ == "__main__":
    updater = BrewFatherUpdater()
    updater.start()
    app.run(host='0.0.0.0')
