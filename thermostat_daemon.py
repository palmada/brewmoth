import traceback

from hardware_control.thermostat import Thermostat

if __name__ == '__main__':

    thermostat = Thermostat()
    try:
        with thermostat:
            thermostat.process.join()
    except KeyboardInterrupt:
        print("Thermostat was interrupted.")
    except BaseException as e:
        print(e)
        traceback.print_exc(e)
