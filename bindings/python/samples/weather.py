#!/usr/bin/env python
from samplebase import SampleBase
from rgbmatrix import graphics
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image
import pyowm
from socket import timeout
import time
import sys
import colour
import datetime
import logging
from logging import handlers 
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S')
file_handler = handlers.RotatingFileHandler('/var/log/weather-python/file.log', maxBytes=(1048576*5), backupCount=7)
file_handler.setFormatter(formatter)
stderr_handler = logging.StreamHandler()
stderr_handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(file_handler)
logger.addHandler(stderr_handler)

MAX_TRIES_API_CALL = 6

class GraphicsTest(SampleBase):
    def __init__(self, *args, **kwargs):
        super(GraphicsTest, self).__init__(*args, **kwargs)
        self.api_tries = 0
        blue = colour.Color('blue')
        red = colour.Color('red')
        self.color_gradient = list(blue.range_to(red, 75))

    def run(self):
        while True:
            self.__determine_brightness()
            self.__get_weather()
            self.matrix.Clear()
            self.__display_current()
            self.__display_image()
            self.__display_todays_low()
            self.__display_todays_high()
            time.sleep(600) # show display for 10 minutes before refreshing

    def __determine_brightness(self):
        hour = int(time.strftime('%H'))
        if 7 <= hour <= 21:
            self.matrix.brightness = 100
        else:
            self.matrix.brightness = 20
    
    def __display_current(self):
        font = graphics.Font()
        font.LoadFont("../../../fonts/7x13.bdf")
        temp_int = round(self.temp.get('temp'))
        text = str(temp_int) + '\u00b0C'
        graphics.DrawText(self.matrix, font, 2, 10, self.__get_color_gradient(temp_int), text)

    def __display_image(self):
        image = Image.open('icons/' + self.__select_image())
        self.matrix.SetImage(image.convert('RGB'), 0, 10)

    def __display_todays_low(self):
        font = graphics.Font()
        font.LoadFont("../../../fonts/5x7.bdf")
        temp_min_int = round(self.temp.get('temp_min'))
        text = '\u2193 ' + str(temp_min_int) + '\u00b0C'
        graphics.DrawText(self.matrix, font, 2, 52,
                          self.__get_color_gradient(temp_min_int), text)

    def __display_todays_high(self):
        font = graphics.Font()
        font.LoadFont("../../../fonts/5x7.bdf")
        temp_max_int = round(self.temp.get('temp_max'))
        text = '\u2191 ' + str(temp_max_int) + '\u00b0C'
        graphics.DrawText(self.matrix, font, 2, 62,
                          self.__get_color_gradient(temp_max_int), text)

    def __get_weather(self):
        key_file = open(".env", "r")
        key = key_file.read().rstrip('\n')
        try:
            owm = pyowm.OWM(key)
            observation = owm.weather_at_id(4887398)  # Chicago
            new_temp = observation.get_weather().get_temperature('celsius')
            new_icon = observation.get_weather().get_weather_icon_name()
        except (pyowm.exceptions.api_response_error.APIResponseError, pyowm.exceptions.api_call_error.APICallTimeoutError) as error:
            logger.exception(error)
            self.api_tries += 1
            if self.api_tries >= MAX_TRIES_API_CALL:
                raise "API call failed 6 times in a row. Will not try again"
            else:
                logger.warning("Will try again in 10 minutes to update weather data. Displaying old data.")
                pass
        except timeout as error:
            logger.warning("socket timeout")
            pass
        else:
            logger.info("api call successful")
            self.api_tries = 0
            self.temp = new_temp
            self.icon = new_icon
        finally:
            key_file.close()

    def __select_image(self):
        icon_map = {
            '01d': 'sunny_day.png',
            '02d': 'partly_cloudy_day.png',
            '03d': 'partly_cloudy_day.png',
            '04d': 'cloudy.png',
            '09d': 'scattered_showers_day.png',
            '10d': 'rain_day.png',
            '11d': 'thunder_storms_day.png',
            '13d': 'snow_day.png',
            '50d': 'mist_day.png',
            '01n': 'clear_night.png',
            '02n': 'partly_cloudy_night.png',
            '03n': 'partly_cloudy_night.png',
            '04n': 'cloudy.png',
            '09n': 'scattered_showers_night.png',
            '10n': 'rain_night.png',
            '11n': 'thunder_storms_night.png',
            '13n': 'snow_night.png',
            '50n': 'mist_night.png'
        }
        return icon_map.get(self.icon, 'rainbow_other.png')

    def __get_color_gradient(self, temp_int):
        # min/max range -30/45 Celsius
        if temp_int < -30:
            index = 0
        elif temp_int > 45:
            index = len(self.color_gradient) - 1
        else:
            index = temp_int + 29
        rgb_255 = tuple([int(round(z * 255))
                         for z in self.color_gradient[index].rgb])
        return graphics.Color(rgb_255[0], rgb_255[1], rgb_255[2])

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logger.error("Uncaught Exception", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception

# Main function
if __name__ == "__main__":
    graphics_test = GraphicsTest()
    if (not graphics_test.process()):
        graphics_test.print_help()
