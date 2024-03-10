#!/usr/bin/env python3.10

"""pyimdbmoviefinder CLI tool."""

import logging
from sys import path
from os.path import dirname
from colorama import init as cinit
from pyimdbmoviefinder.utils import LoggingColorFilter
path.append(dirname(__file__))

cinit()
ch = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(levelname)8s %(filename)s | %(message)s')
ch.setFormatter(formatter)

logger = logging.getLogger('pyimdbmoviefinder')
logger.addHandler(ch)
logger.setLevel(logging.DEBUG)  # Change this for more logging
logger.addFilter(LoggingColorFilter())
