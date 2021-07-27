import json
import os

from flask import Flask, request
from flask_cors import CORS
# noinspection PyUnresolvedReferences
from systemd import journal

from brewmoth_server.brewfather import BrewFatherUpdater
from hardware_control.temperature_sensors import *
from hardware_control.thermostat import read_settings_file, write_to_settings_file
from utilities.constants import *
from utilities.formatters import timestamp

BATCH_FOLDER = MOTH_LOCATION + 'batches'
ALLOWED_EXTENSIONS = {'txt', 'json'}

app = Flask(__name__)
CORS(app)


@app.before_first_request
def init_brewfather():
    updater = BrewFatherUpdater()
    updater.start()


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
            data: dict = request.get_json()

            if CLI_SET_TEMP in data:
                set_point = data[CLI_SET_TEMP]

                journal.write("Received temperature request:" + str(data))

                try:
                    set_point = float(set_point)
                except ValueError:
                    return "Error parsing requested temperature"

                settings = read_settings_file()

                thermostat_on = settings[SP_STATE] == SP_ON

                settings[SP_TEMP] = set_point
                settings[SP_STATE] = SP_ON

                if not thermostat_on:
                    return_message = "Set temperature control to " + str(set_point)
                else:
                    return_message = "Changed temperature set point to " + str(set_point)

                write_to_settings_file(settings)

                return return_message

            elif data == CLI_GET_TEMP:
                return {
                    CLI_FRIDGE: read_temp(TEMP_FILE),
                    CLI_ROOM: read_temp(ROOM_TEMP_FILE)
                }
            elif data == CLI_OFF:
                settings = read_settings_file()
                thermostat_on = settings[SP_STATE] == SP_ON

                if thermostat_on:
                    settings[SP_STATE] = SP_OFF
                    write_to_settings_file(settings)
                    return "Turned off temperature control."
                else:
                    return "Was asked to turn off, but temperature control is already off."
            else:
                return "Got the following post: " + str(data) + ", but don't know what to do with it."

        else:
            return "Not a correct post"

    except Exception as e:
        return "Exception: " + str(e)


if __name__ == "__main__":
    app.run(host='0.0.0.0')
