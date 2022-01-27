import json
import traceback

from hardware_control.thermostat import Thermostat
from utilities.constants import CONFIG_FILE

if __name__ == '__main__':

    with open(CONFIG_FILE, 'r') as config_file:
        file_contents = config_file.read()
        config = json.loads(file_contents)

    thermostat = Thermostat(config)

    try:
        with thermostat:
            thermostat.process.join()
    except KeyboardInterrupt:
        print("Thermostat was interrupted.")
    except BaseException as e:
        print(e)
        traceback.print_exc(e)
