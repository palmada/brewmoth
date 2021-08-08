import json
import sys

from brewmoth_server.brewfather import brewfather_data_import

if __name__ == '__main__':
    if len(sys.argv) < 2:
        raise EnvironmentError("Need at least one argument with the import JSON")

    file_location = sys.argv[1]

    with open(file_location, 'r+') as brewfather_json:
        brewfather_json.seek(0)
        if brewfather_json:
            json_string = brewfather_json.read()

            data = json.loads(json_string)

            set_points = brewfather_data_import(data)

            for set_point in set_points:
                print(set_point.to_json())
