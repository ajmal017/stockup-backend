import socket
import motor

DEBUG = False if 'stockup' in socket.gethostname() else True

TEST_IPAD_TOKEN = 'bead382dc014c9f73246f9f5b6d606ddf87b1237701eca8e743cf3641089c79d'


def debug_log(logger, msg):
    if DEBUG:
        logger.info(msg)


def datetime_repr():
    return '%Y-%m-%dT%H:%M:%S'