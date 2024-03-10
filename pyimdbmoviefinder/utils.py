import sys
import time
import threading
import logging

class bcolors:
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
      logging.DEBUG: bcolors.OKCYAN,
      logging.WARNING: bcolors.WARNING,
      logging.ERROR: bcolors.FAIL,
      logging.INFO: bcolors.OKBLUE
   }

   def filter(self, record):
      record.raw_msg = record.msg
      color = self.color_by_level.get(record.levelno)
      if color:
        record.msg = f'{color}{record.msg}{bcolors.ENDC}'
      return True

class Spinner:
    busy = False
    delay = 0.1

    @staticmethod
    def spinning_cursor():
        while 1: 
            for cursor in '|/-\\': yield cursor

    def __init__(self, delay=None):
        self.spinner_generator = self.spinning_cursor()
        if delay and float(delay): self.delay = delay

    def spinner_task(self):
        while self.busy:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')
            sys.stdout.flush()

    def __enter__(self):
        self.busy = True
        threading.Thread(target=self.spinner_task).start()

    def __exit__(self, exception, value, tb):
        self.busy = False
        time.sleep(self.delay)
        if exception is not None:
            return False