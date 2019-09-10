#!/usr/bin/env python
import sys
import logging
import logging.config
from weather import Weather

def handle_exception(exc_type, exc_value, exc_traceback):
   if issubclass(exc_type, KeyboardInterrupt):
       sys.__excepthook__(exc_type, exc_value, exc_traceback)
       return

   logger.error("Uncaught Exception", exc_info=(
       exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception

if __name__ == "__main__":
    logging.config.fileConfig('mylogger.conf', disable_existing_loggers=False)
    logger = logging.getLogger('mylogger')
    weather = Weather()
    if (not weather.process()):
        weather.print_help()
