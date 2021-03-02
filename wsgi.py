import sys

from utilities.constants import MOTH_LOCATION
from brewmoth_server.brewmoth import app

sys.path.append(MOTH_LOCATION)


if __name__ == "__main__":
    app.run()
