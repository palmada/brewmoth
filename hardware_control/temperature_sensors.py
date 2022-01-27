import time

# noinspection PyUnresolvedReferences
from systemd import journal
from utilities.constants import CFG_SENSORS, ERROR_NO_SENSORS, CFG_SENSOR_SERIAL, NAME, TYPE


def sensor_location(sensor_id: str):
    """
    From a given sensor serial (e.g. 28-3c01b556f57f) construct a full on disk location to the temperatures file
     for the sensor.
    """
    return '/sys/bus/w1/devices/' + sensor_id + '/w1_slave'


def read_temps(config: dict) -> dict:
    """
    Returns a dictionary of temperature reads, with sensor names as the keys.

    :param config: the contents of a config.json type file, including a CFG_SENSORS entry
    """

    temperatures = dict()
    for sensor in config[CFG_SENSORS]:
        try:
            file = sensor_location(sensor[CFG_SENSOR_SERIAL])
            temp = str(read_temp(file))
            temperatures[sensor[NAME]] = temp
        except Exception as e:
            journal.write("Failed to get reading '" + sensor + "':", str(e))

    if not temperatures:
        message = 'read_temps_to_dict: ' + ERROR_NO_SENSORS
        journal.write(message)
        raise Exception(message)

    return temperatures


def get_location_for_sensor(config_dictionary: dict, required_sensor_type: str) -> str:
    """
    For a given sensor type, return the on disk location of the sensor data
    """
    if CFG_SENSORS not in config_dictionary:
        raise Exception("No 'Temperature sensors' entry found in config.json file!")

    for sensor in config_dictionary[CFG_SENSORS]:
        if sensor[TYPE] is required_sensor_type:
            return sensor_location(sensor[CFG_SENSOR_SERIAL])

    raise Exception(required_sensor_type + " sensor not found in config.json file!")


def check_sensor_types_are_present(config_dictionary: dict, *sensor_types: str):
    """
    Checks if the given dictionary contains the given sensor types.
    """
    if CFG_SENSORS not in config_dictionary:
        raise Exception("No 'Temperature sensors' entry found in config.json file!")

    for sensor_type in sensor_types:
        failed = True
        for sensor in config_dictionary[CFG_SENSORS]:
            if sensor[TYPE] is type:
                failed = False

        if failed:
            raise Exception(sensor_type + " sensor not found in config.json file!")


def read_temp_raw(device_file):
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines


def read_temp(device_file):
    lines = read_temp_raw(device_file)
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw(device_file)
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c
