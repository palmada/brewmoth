from datetime import datetime
from enum import Enum
from typing import List

from constants import SP_TEMP, SP_DATE, SP_TYPE, SP_TARGET

TIME_STAMP_FORMAT = '%d/%m/%Y %H:%M'

'''
This module contains functions to parse temperature set points in JSON files and to define
temperature profiles that vary over time. 

The below JSON shows an example of how to structure a temperature set point that varies over time.

The example should result in the following profile:
1 - The temperature will be held at 20°C for a day
2 - The temperature will then ramp up from 20°C to 25°C over two days
3 - Afterwards, the temperature will crash down to 12°C as fast as the system can

 
Notes:
 - All of the functions in this module are unit agnostic; Celsius is used only as an example.
 - To specify a ramp, simply include two consecutive set points, and on the second set point include
  'Type': 'Ramp'
 - If the temperature target of the first time point on a ramp is different from whatever was set previously,
   this will result in a temperature step. If this is not your desired outcome, make sure the first time point 
   on the ramp matches whatever was set previously. To see what we mean by this, just look at the first
   two set points on the example JSON. 
 - For crashing/stepping (changing temperature as fast as the system can go), you do not need to set a type.
 - The order of the time point list doesn't actually matter as they will be sorted correctly by the parser.
'''

example_json = {
    "Temperature": [
        {'Date': '05/08/2021 17:30', 'Target': 20},
        {'Date': '06/08/2021 17:30', 'Target': 20},
        {'Date': '08/08/2021 17:30', 'Target': 25, 'Type': 'Ramp'},
        {'Date': '09/08/2021 18:30', 'Target': 12},
    ],
    "Sampling": 5,
    "Heat Tolerance": 1,
    "Cool Tolerance": 0.1,
    "State": "On"
}


class SetPointType(Enum):
    CRASH = 1
    RAMP = 2


class SetPoint:
    """
    Represents one temperature set point on our temperature profile.
    """

    def __init__(self, json: dict):
        self.temp = json[SP_TARGET]
        self.date = datetime.strptime(json[SP_DATE], TIME_STAMP_FORMAT)
        if SP_TYPE in json:
            self.type = SetPointType.RAMP
        else:
            self.type = SetPointType.CRASH


def time_difference(compared_set_point: SetPoint, time_stamp: datetime) -> float:
    """
    Gets the time difference between a set point and a date time

    :param time_stamp: Set point we're comparing against
    :param compared_set_point: datetime we're comparing
    :return: The difference in seconds
    """
    return (time_stamp - compared_set_point.date).total_seconds()


def get_list_set_points(json: List[dict]) -> List[SetPoint]:
    """
    Converts a JSON entry of set points into a list of SetPoint objects, sorted by their time stamps.

    :param json: A parsed "Temperature" entry, as a list of JSON objects
    :return:
    """
    set_points = []
    for entry in json:
        set_points.append(SetPoint(entry))

    # We now sort the time points by their time stamps. We use the first on the list as a random radix
    first = set_points[0]

    def sort_key(value: SetPoint):
        return time_difference(value, first.date)

    set_points = sorted(set_points, key=sort_key, reverse=True)

    return set_points


def get_temp_point(first_set_point: SetPoint, second_set_point: SetPoint, time_stamp: datetime) -> float:
    """
    For a given pair of set points and a date and time, this function returns what is the temperature
    that should be at the given date and time

    :param first_set_point: 1st temperature set point; has to be earlier in time than the 2nd set point.
    :param second_set_point: 2nd temperature set point; has to be later in time than the 1st set point.
    :param time_stamp: A datetime object.
    :return: The temperature that should be set at the given time, according to the two set points.
             If the given time is earlier than the two set points, then returns the first set point temp.
             If the given time is later than the two set points, then returns the second set point temp.
    """
    time_to_next = time_difference(second_set_point, time_stamp)
    time_to_previous = time_difference(first_set_point, time_stamp)

    # If we found a time range where our current time point fits
    if time_to_next < 0 and time_to_previous > 0:
        if second_set_point.type is SetPointType.RAMP:
            ramp_time = time_to_previous - time_to_next

            previous_temp = first_set_point.temp
            next_temp = second_set_point.temp
            ramp_temp = next_temp - previous_temp

            ramp = ramp_temp / ramp_time
            target_temp = previous_temp + (time_to_previous * ramp)
        else:
            target_temp = first_set_point.temp
    elif time_to_next > 0:
        target_temp = second_set_point.temp
    else:
        target_temp = first_set_point.temp

    return target_temp


def parse_set_point(set_points: List[SetPoint], current_time: datetime):
    """
    From a given list of set points, determine what is the target temperature at the given time.

    :param set_points: List of SetPoints defining a temperature profile. The list must already be sorted;
                       use the get_list_set_points to parse a JSON and sort the list.
    :param current_time: The current time as a datetime
    :return: The target temperature.
    """

    # This will be used in the loops to store what was the set point in the previous index of the loop
    previous_set_point = set_points[0]
    time_to_previous = time_difference(previous_set_point, current_time)

    # We create a signal to indicate if we didn't get the target temp
    target_temp = -100

    if time_to_previous > 0:
        for next_set_point in set_points[1:]:
            time_to_next = time_difference(next_set_point, current_time)
            time_to_previous = time_difference(previous_set_point, current_time)

            # If we found a time range where our current time point fits
            if time_to_next < 0 and time_to_previous > 0:
                target_temp = get_temp_point(previous_set_point, next_set_point, current_time)
                break

            previous_set_point = next_set_point

        # If we've cycled through the points and we haven't found a temp, then likely
        # the given time point refers to a point after the temperature profile.
        # In that case, we just use whatever was the last temperature set point,
        # which will be recorded in the previous_set_point variable
        if target_temp == -100:
            target_temp = previous_set_point.temp

    # Else, the given time point refers to a point before the list of SetPoints,
    # so we just use the first SetPoint in the list.
    else:
        target_temp = previous_set_point.temp

    if target_temp == -100:
        raise ValueError("Could not determine the correct temperature")

    return target_temp

