import sys

from brewmoth_server.brewmoth import app
from utilities.constants import MOTH_LOCATION
sys.path.append(MOTH_LOCATION)

if __name__ == "__main__":
    app.run()
