#! /usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys
import os
from os.path import join
from logging.handlers import TimedRotatingFileHandler

project_root = os.path.dirname(os.path.abspath(__file__))
FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
LOG_FILE = join(project_root, "logs/game.log")


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_file_handler():
    file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name):
    app_logger = logging.getLogger(logger_name)
    app_logger.setLevel(10)  # Debug
    app_logger.addHandler(get_console_handler())
    app_logger.addHandler(get_file_handler())
    app_logger.propagate = False
    return app_logger
