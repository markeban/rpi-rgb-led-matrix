import sys
import logging
from logging import handlers
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
file_handler = handlers.RotatingFileHandler(
    '/var/log/weather-python/file.log', maxBytes = (1048576*5), backupCount = 7)
    # '/Users/mark/raspberry_pi/rpi-rgb-led-matrix/bindings/python/samples/file.log', maxBytes=(1048576*5), backupCount=7)
file_handler.setFormatter(formatter)
stderr_handler = logging.StreamHandler()
stderr_handler.setFormatter(formatter)
