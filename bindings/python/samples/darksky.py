#!/usr/bin/env python
import requests
from mylogger import logging, file_handler, stderr_handler
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(stderr_handler)

LATITUDE = '41.974925'
LONGITUDE = '-87.662873'

class DarkSky:
  def __init__(self):
      self.json_response = None
      key_file = open("darksky.env", "r")
      self.api_key = key_file.read().rstrip('\n')

  def get_data(self): 
      payload = dict(
        exclude=['minutely', 'hourly', 'alerts', 'flags'],
        units='si'
      )
      try:
          raw_response = requests.get(
            'https://api.darksky.net/forecast/' + self.api_key + '/' + LATITUDE + ',' + LONGITUDE,
            params = payload,
            timeout = 10
          )
      except requests.exceptions.RequestException as error:
          logger.warning("Unable to get DarkSky Data: " + error)
          return False
      else:
          logger.info("get_data API call to DarkSky successful")
          self.json_response = raw_response.json()
          self

  def is_success(self):
      return True if self.json_response else False

  def current_temp(self):
      return self.json_response["currently"]["temperature"]

  def todays_high(self):
      return self.json_response["daily"]["data"][0]["temperatureHigh"]

  def todays_low(self):
      return self.json_response["daily"]["data"][0]["temperatureLow"]

  def icon(self):
      return self.json_response["currently"]["icon"]
  

