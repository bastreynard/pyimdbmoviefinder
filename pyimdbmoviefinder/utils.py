'''
Utility module for logging filtering and spinner CLI
'''

import sys
import time
import threading
import logging


class BColors:
    '''
    Class holding a few ANSI codes for colors
    '''
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


class LoggingColorFilter(logging.Filter):
    """
    Class for setting specific colors to logging
    """

    color_by_level = {
        logging.DEBUG: BColors.OKCYAN,
        logging.WARNING: BColors.WARNING,
        logging.ERROR: BColors.FAIL,
        logging.INFO: BColors.OKBLUE
    }

    def filter(self, record):
        record.raw_msg = record.msg
        color = self.color_by_level.get(record.levelno)
        if color:
            record.msg = f'{color}{record.msg}{BColors.ENDC}'
        return True


class Spinner:
    """Spinner class for showing a loading spinner in the command line
    """
    busy = False
    delay = 0.1

    @staticmethod
    def spinning_cursor():
        """Generates the cursor

        Yields:
            str: The cursor char value
        """
        while 1:
            for cursor in '|/-\\':
                yield from cursor

    def __init__(self, delay:int =None):
        """Constructor

        Args:
            delay (int, optional): Delay between rotations in seconds. Defaults to None.
        """
        self.spinnerGenerator = self.spinning_cursor()
        if delay and float(delay):
            self.delay = delay

    def spinner_task(self):
        """Task for running the spinner
        """
        while self.busy:
            sys.stdout.write(next(self.spinnerGenerator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')
            sys.stdout.flush()

    def __enter__(self):
        """Entry of Task
        """
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def __exit__(self, exception, value, tb):
        """Exit of task

        Args:
            exception : exception
            value : value
            tb : tb

        Returns:
            bool: True if exception occured, False otherwise
        """
        self.busy = False
        time.sleep(self.delay)
        return exception is None
