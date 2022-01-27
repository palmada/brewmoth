import sys

from brewmoth_server import brewmoth
from brewmoth_server.brewmoth import app
from utilities.constants import MOTH_LOCATION
# noinspection PyUnresolvedReferences
from systemd import journal

sys.path.append(MOTH_LOCATION)

journal.write("Initializing Brewmoth...")
# This file should hopefully only be called once by the WSGI service control,
# meaning we only initialize our threads once
brewmoth.initialize()

if __name__ == "__main__":
    app.run()
