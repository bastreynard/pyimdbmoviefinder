#!/usr/bin/env python3.10

"""pyimdbmoviefinder CLI tool."""

from sys import path
from os.path import dirname
path.append(dirname(__file__))

import logging
from colorama import init as cinit
from utils import LoggingColorFilter
cinit()
ch = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s %(levelname)8s %(filename)s | %(message)s')
ch.setFormatter(formatter)

logger = logging.getLogger('pyimdbmoviefinder')
logger.addHandler(ch)
logger.setLevel(logging.DEBUG)  # Change this for more logging
logger.addFilter(LoggingColorFilter())