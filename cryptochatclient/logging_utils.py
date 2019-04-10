"""
Common logging functionality
"""

import logging
import os


class OneLineExceptionFormatter(logging.Formatter):
    """
    Formatter used to insure each log-entry is one line
    (insures one entry-per-log for some logging environments that divide on newline)
    """

    def formatException(self, ei):
        """
        Make sure exception-tracebacks end up on a single line.
        """
        result = super(OneLineExceptionFormatter, self).formatException(ei)
        return repr(result)

    def format(self, record):
        """
        Convert newlines in each record to |
        """
        fmt_str = super(OneLineExceptionFormatter, self).format(record)
        if record.exc_text:
            fmt_str = fmt_str.replace('\n', '') + '|'
        return fmt_str


def init_logging():
    """Setup root logger handler."""
    logger = logging.getLogger()
    uuid = os.uname().nodename
    uuid += ":%d" % os.getpid()
    log_fmt = uuid + " %(asctime)s %(name)s: [%(levelname)s] %(message)s"
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = OneLineExceptionFormatter(log_fmt)
        handler.setFormatter(formatter)
        logger.addHandler(handler)


def get_logger(name):
    """
    Set logging level and return logger.
    """
    logger = logging.getLogger(name)
    level = os.getenv('LOGGING_LEVEL', "INFO")
    logger.setLevel(getattr(logging, level, logging.INFO))
    return logger
