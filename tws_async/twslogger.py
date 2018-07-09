import logging
import time

from logging.handlers import TimedRotatingFileHandler


# ----------------------------------------------------------------------
def create_timed_rotating_log(path, log_data):
    """"""

    logger = logging.getLogger("Rotating Log")
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = TimedRotatingFileHandler(path,
                                           when="H",
                                           interval=1,
                                           backupCount=0)
        logger.addHandler(handler)

    logger.info(log_data)
