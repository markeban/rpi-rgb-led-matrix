#!/usr/bin/env python
import logging
import logging.config
from weather import Weather

if __name__ == "__main__":
    logging.config.fileConfig('mylogger.conf')
    logger = logging.getLogger('mylogger')
    weather = Weather()
    if (not weather.process()):
        weather.print_help()
