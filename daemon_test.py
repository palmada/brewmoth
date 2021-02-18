import signal

import daemon
import lockfile

from spam import (
    initial_program_setup,
    do_main_program,
    program_cleanup,
    reload_program_config,
)

context = daemon.DaemonContext(
    working_directory='/home/palmada/gpio-ctl',
    umask=0o002,
    pidfile=lockfile.FileLock('/var/run/spam.pid'),
    )

context.signal_map = {
    signal.SIGTERM: program_cleanup,
    signal.SIGHUP: 'terminate',
    signal.SIGUSR1: reload_program_config,
    }

context.gid = 1001

important_file = open('spam.data', 'w')
interesting_file = open('eggs.data', 'w')
context.files_preserve = [important_file, interesting_file]  # Files meant to stay open after

initial_program_setup()

if __name__ == '__main__':
    with context:
        print("Context opened")
        do_main_program(important_file)
        print("Did main program")
    print("Finished")