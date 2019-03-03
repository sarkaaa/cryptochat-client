#!/usr/bin/env python3
"""
Main cryptochat-client module
"""

import os
import sys

import app
from logging_utils import init_logging, get_logger

LOGGER = get_logger(__name__)
CLIENT_VERSION = os.environ.get('VERSION')


def show_error_and_exit(error_text):
    raise NotImplementedError()


def check_requirements():
    raise NotImplementedError()


def main():
    init_logging()
    LOGGER.info("Starting (version %s).", CLIENT_VERSION)
    status = app.run()
    sys.exit(status)


if __name__ == '__main__':
    main()
