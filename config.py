TEST_IPAD_TOKEN = 'bead382dc014c9f73246f9f5b6d606ddf87b1237701eca8e743cf3641089c79d'

COOKIE_KEY = "2BGQuaOqQwOOjPRhuYwgk95iG767I0xPmstRiVNMzDg="

DEBUG = True


def debug_log(logger, msg):
    if DEBUG:
        logger.info(msg)


def datetime_repr():
    return '%Y-%m-%dT%H:%M:%S'
