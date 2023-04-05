import os
from pathlib import Path

from utilities.constants import READS_FOLDER
from utilities.formatters import timestamp


def create_time_stamped_csv():
    Path(READS_FOLDER).mkdir(parents=True, exist_ok=True)

    return open(os.path.join(READS_FOLDER, timestamp() + ".csv"), "w")
