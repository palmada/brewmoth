import pigpio

pins = pigpio.pi()

if not pins.connected:
    raise Exception("Could not connect to pigpio")

fan_pin = 19
frequency = 25000  # 25 kHz
max_duty_cycle = 1000000  # from pigpiod


def set_fan_speed(speed):

    if speed < 0:
        speed = 0

    if 0 < speed < 0.1:
        speed = 0.1

    if speed > 1:
        speed = 1

    speed = int(speed * max_duty_cycle)

    pins.hardware_PWM(fan_pin, frequency, speed)
