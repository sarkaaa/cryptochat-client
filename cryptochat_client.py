#!/usr/bin/env python3
"""
Main cryptochat-client module
"""

import os
import sys

from cryptochatclient import app
from cryptochatclient.logging_utils import init_logging, get_logger

LOGGER = get_logger(__name__)
CLIENT_VERSION = os.environ.get('VERSION')
os.environ['LOGGING_LEVEL'] = "DEBUG"


def show_error_and_exit(error_text):
    """
    Show error.
    :param error_text:
    :return:
    """
    raise NotImplementedError()

def check_requirements():
    """
    Check requirements.
    :param error_text:
    :return:
    """
    raise NotImplementedError()

def main():
    """
    Main function.
    :param error_text:
    :return:
    """
    init_logging()
    LOGGER.info("Starting (version %s).", CLIENT_VERSION)
    sys.exit(app.run())

if __name__ == '__main__':
    main()
