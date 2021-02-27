from datetime import datetime


def timestamp():
    now = datetime.now()

    return "{0}-{1}-{2}_{3}.{4}.{5}".format(now.year,
                                            f'{now.month:02}',
                                            f'{now.day:02}',
                                            f'{now.hour:02}',
                                            f'{now.minute:02}',
                                            f'{now.second:02}')


if __name__ == '__main__':
    print(timestamp())
