import json
import os

from flask import Flask, request
from flask_cors import CORS
# noinspection PyUnresolvedReferences
from systemd import journal

from brewmoth_server.brewfather import BrewFatherUpdater, brewfather_data_import
from hardware_control.temperature_sensors import *
from hardware_control.thermostat import read_settings_file, write_to_settings_file
from utilities.constants import *
from utilities.formatters import timestamp

BATCH_FOLDER = MOTH_LOCATION + 'batches'
ALLOWED_EXTENSIONS = {'txt', 'json'}

app = Flask(__name__)
CORS(app)

updater = BrewFatherUpdater()
updater.start()


@app.route("/brewfather", methods=['GET', 'POST'])
def save_post():
    if request.method == 'POST':

        if request.is_json:
            received_json = request.get_json()
            time_stamp = timestamp() + ".batch"
            batch_file_location = os.path.join(BATCH_FOLDER, time_stamp)
            file = open(batch_file_location, "w")

            # noinspection PyBroadException
            try:
                set_points = brewfather_data_import(received_json)

                json_set_points = []
                for set_point in set_points:
                    json_set_points.append(set_point.to_json())

                settings = read_settings_file()
                settings[SP_TEMP] = json_set_points
                write_to_settings_file(settings)
            except Exception as e:
                journal.write("Exception while parsing brewfather batch.")
                journal.write(str(e))

            file.write(json.dumps(received_json))
            file.close()

            journal.write("Received Brewfather batch" + batch_file_location)
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

                journal.write(return_message)

                return return_message

            elif data == CLI_GET_TEMP:
                temps = {
                    CLI_FRIDGE: read_temp(TEMP_FILE),
                    CLI_ROOM: read_temp(ROOM_TEMP_FILE)
                }

                journal.write("Received request for temps, returning " + str(temps))

                return temps
            elif data == CLI_OFF:
                settings = read_settings_file()
                thermostat_on = settings[SP_STATE] == SP_ON

                if thermostat_on:
                    settings[SP_STATE] = SP_OFF
                    write_to_settings_file(settings)
                    return_message = "Turned off temperature control."
                else:
                    return_message = "Was asked to turn off, but temperature control is already off."

                journal.write(return_message)
                return return_message
            else:
                message = "Got the following post: " + str(data) + ", but don't know what to do with it."
                journal.write(message)
                return message

        else:
            message = "Received an incorrect post"
            journal.write(message)
            return message

    except Exception as e:
        message = "Exception: " + str(e)
        journal.write(message)
        return message


if __name__ == "__main__":
    app.run(host='0.0.0.0')
