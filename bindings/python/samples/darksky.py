#!/usr/bin/env python
import requests
from datetime import datetime
import logging
logger = logging.getLogger(__name__)

################ Chicago ###################
LATITUDE = '41.974925'
LONGITUDE = '-87.662873'
############################################

class DarkSky:
  def __init__(self):
      self.json_response = None
      key_file = open("/home/pi/projects/weather-python/rpi-rgb-led-matrix/bindings/python/samples/darksky.env", "r")
      self.api_key = key_file.read().rstrip('\n')
      self.__get_data()

  def __get_data(self):
      payload = dict(
        exclude=['minutely', 'alerts', 'flags'],
        units='si'
      )
      try:
          raw_response = requests.get(
            'https://api.darksky.net/forecast/' + self.api_key + '/' + LATITUDE + ',' + LONGITUDE,
            params = payload,
            timeout = 10
          )
      except requests.exceptions.RequestException as error:
          logger.warning("Unable to get DarkSky Data: " + str(error))
          return False
      else:
          logger.info("API call to DarkSky status code: " + str(raw_response.status_code))
          if int(raw_response.status_code) != 200: return False
          self.json_response = raw_response.json()
          self

  def is_success(self):
      return True if self.json_response else False

  def current_temp(self):
      return self.json_response["currently"]["temperature"]

  def todays_high(self):
      return self.__hourly_temp_range()[-1]

  def todays_low(self):
      return self.__hourly_temp_range()[0]

  def icon(self):
      return self.json_response["currently"]["icon"]

  def __hourly_temp_range(self):
      # we don't want the first (most recent) forecast, as it's for the current hour
      # which is already covered by the current temp
      remaining_forecasts = self.json_response["hourly"]["data"][1:self.__hours_till_midnight()]
      forecast_temps = list(map(self.__select_temp, remaining_forecasts))
      combined_temps = [self.current_temp()] + forecast_temps
      combined_temps.sort()
      return combined_temps

  def __hours_till_midnight(self):
      now = datetime.now()
      current_hour = int(now.strftime("%H"))
      return 24 - current_hour

  def __select_temp(self, hourly_forecast):
      return int(hourly_forecast["temperature"])

# def handle_exception(exc_type, exc_value, exc_traceback):
#    if issubclass(exc_type, KeyboardInterrupt):
#        sys.__excepthook__(exc_type, exc_value, exc_traceback)
#        return

#    logger.error("Uncaught Exception", exc_info=(
#        exc_type, exc_value, exc_traceback))

# Main function
# if __name__ == "__main__":
# logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)
# logger.addHandler(file_handler)
# logger.addHandler(stderr_handler)
# sys.excepthook = handle_exception
