from datetime import datetime


def timestamp():
    now = datetime.now()

    return "{0}.{1}.{2}_{3}:{4}:{5}".format(now.year, now.month, now.day,
                                            now.hour, now.minute, now.second)
