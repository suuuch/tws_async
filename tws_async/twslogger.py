import logging
import time

from logging.handlers import TimedRotatingFileHandler


# ----------------------------------------------------------------------
import os


def create_timed_rotating_log(log_data, path):
    """"""

    logger = logging.getLogger("Rotating Log")
    logger.setLevel(logging.INFO)
    logger.propagate = False
    if not logger.handlers:
        path = os.path.join(path,log_data.get('symbol')+'.logs')
        handler = TimedRotatingFileHandler(path,
                                           when="H",
                                           interval=1,
                                           backupCount=0)
        logger.addHandler(handler)

    logger.info(log_data)
