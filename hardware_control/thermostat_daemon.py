import json
import traceback

from hardware_control.thermostat import Thermostat
from utilities.constants import CONFIG_FILE

# You might be tempted to put this in a sub-package, but it needs to be here to function properly.
# The thermostat also always needs its own service, so it stops cleanly.

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
        traceback.print_exc()
