import os
import glob
import time
import requests

url = 'http://log.brewfather.net/stream?id=OniWOwAOjMnLsM'
json = {
    "name": "Moth",  # Required field, this will be the ID in Brewfather
    "temp": -5,
    "temp_unit": "C",  # C, F, K
}

os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
room_temp_file = base_dir + '28-3c01b5566db7/w1_slave'
temp_file = base_dir + '28-3c01b556f57f/w1_slave'


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


if __name__ == '__main__':
    try:
        while True:
            try:
                try:
                    room_temp = str(read_temp(room_temp_file))
                    json["ext_temp"] = room_temp
                except:
                    print("Failed to get room temp")

                try:
                    fermenter_temp = str(read_temp(temp_file))
                    json["temp"] = fermenter_temp
                except:
                    print("Failed to get fridge temp")

                if "ext_temp" not in json and "temp" not in json:
                    raise Exception("Failed to get either temperature")

                requests.post(url, data=json)
                time.sleep(900)
            except:
                print("Error")
    except KeyboardInterrupt:
        print("\nExiting.")
