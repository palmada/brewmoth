from time import sleep

import pigpio

pins = pigpio.pi()


def pin_test(pin1, pin2):
    pins.write(pin1, 1)
    pins.write(pin2, 1)

    sleep(1)

    pins.write(pin1, 0)
    pins.write(pin2, 0)


print("Testing cooling")
pin_test(5, 27)

print("Testing heating")
pin_test(22, 25)

print("Le fin.")
