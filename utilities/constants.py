MOTH_LOCATION = '/brewmoth/'
SET_POINT_FILE = MOTH_LOCATION + "/set_point.json"
READS_FOLDER = MOTH_LOCATION + 'temp-reads'

SP_STATE = "State"
SP_TEMP = "Temperature"
SP_DATE = "Date"
SP_TARGET = "Target"
SP_TYPE = "Type"
SP_RAMP = "Ramp"
SP_SAMPLING = "Sampling"
# The tolerances how many degrees the temperature is off before starting to heat or cool
SP_HEAT_TOLERANCE = "Heat Tolerance"
SP_COOL_TOLERANCE = "Cool Tolerance"
SP_ON = "On"
SP_OFF = "Off"

CLI_URL = 'http://127.0.0.1:555/cli'
CLI_GET_TEMP = 'Get temperatures'
CLI_SET_TEMP = 'Set temperature'
CLI_RECORD = 'Record thermostat changes'
CLI_OFF = 'Turn off temperature control'
CLI_FRIDGE = 'Fridge temperature'
CLI_ROOM = 'Room temperature'
