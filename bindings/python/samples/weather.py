#!/usr/bin/env python
from samplebase import SampleBase
from rgbmatrix import graphics
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image
from darksky import DarkSky
import time
import colour
import datetime
import subprocess
import logging
logger = logging.getLogger(__name__)

DATA_DELAY_REFRESH_LIMIT = 3
CALL_INTERVAL_SECONDS = 600 # 10 minutes

class Weather(SampleBase):
    def __init__(self, *args, **kwargs):
        super(Weather, self).__init__(*args, **kwargs)
        self.current_temp = None
        self.api_tries = 0
        blue = colour.Color('blue')
        red = colour.Color('red')
        self.color_gradient = list(blue.range_to(red, 75))

    def run(self):
        while True:
            self.__determine_brightness()
            self.__get_weather()
            self.__display_current()
            self.__display_image()
            self.__display_todays_low()
            self.__display_todays_high()
            time.sleep(CALL_INTERVAL_SECONDS)

    def __determine_brightness(self):
        hour = int(time.strftime('%H'))
        if 7 <= hour <= 21:
            self.matrix.brightness = 70
        else:
            self.matrix.brightness = 10
    
    def __display_current(self):
        font = graphics.Font()
        font.LoadFont("/home/pi/projects/weather-python/rpi-rgb-led-matrix/fonts/7x13.bdf")
        temp_int = round(self.current_temp)
        text = str(temp_int) + '\u00b0C'
        graphics.DrawText(self.matrix, font, 2, 10, self.__get_color_gradient(temp_int), text)

    def __display_image(self):
        image = Image.open('/home/pi/projects/weather-python/rpi-rgb-led-matrix/bindings/python/samples/icons/' + self.__select_image())
        self.matrix.SetImage(image.convert('RGB'), 0, 10)

    def __display_todays_low(self):
        font = graphics.Font()
        font.LoadFont("/home/pi/projects/weather-python/rpi-rgb-led-matrix/fonts/5x7.bdf")
        temp_min_int = round(self.todays_low)
        text = '\u2193 ' + str(temp_min_int) + '\u00b0C'
        graphics.DrawText(self.matrix, font, 2, 52,
                          self.__get_color_gradient(temp_min_int), text)

    def __display_todays_high(self):
        font = graphics.Font()
        font.LoadFont("/home/pi/projects/weather-python/rpi-rgb-led-matrix/fonts/5x7.bdf")
        temp_max_int = round(self.todays_high)
        text = '\u2191 ' + str(temp_max_int) + '\u00b0C'
        graphics.DrawText(self.matrix, font, 2, 62,
                          self.__get_color_gradient(temp_max_int), text)

    def __get_weather(self):
        dk = DarkSky()
        if dk.is_success():
            logger.info('API success on attempt: ' + str(self.api_tries) + ' current_temp: ' + str(dk.current_temp()) + ' todays_low: ' +
                        str(dk.todays_low()) + ' todays_high: ' + str(dk.todays_high()) + ' icon: ' + str(dk.icon()))
            self.current_temp = dk.current_temp()
            self.todays_low = dk.todays_low()
            self.todays_high = dk.todays_high()
            self.icon = dk.icon()
            self.api_tries = 0
        else:
            self.api_tries += 1
            if self.api_tries >= DATA_DELAY_REFRESH_LIMIT or self.current_temp is None:
                self.__reset_os_network_interface()
                now = datetime.datetime.now()
                try_again_time = now + datetime.timedelta(seconds=CALL_INTERVAL_SECONDS)
                logger.warning(
                    "failed to get weather data after " + str(self.api_tries) + " attempt(s). Will try again in " + str(round(CALL_INTERVAL_SECONDS/60)) + " minutes (at " + try_again_time.strftime("%d-%b-%y %H:%M:%S") + ")"
                )
                self.__display_data_failure(try_again_time)
                time.sleep(CALL_INTERVAL_SECONDS)
                self.matrix.Clear()
                self.__get_weather()
            else:
                logger.warning("Attempt: " + str(self.api_tries) + ". Will try again in " + str(round(CALL_INTERVAL_SECONDS/60)) + " minutes to update weather data. Displaying old data.")
                pass
        self.matrix.Clear()

    def __reset_os_network_interface(self):
        process = subprocess.run(['sudo', '/sbin/wpa_cli', '-iwlan0','reassociate'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if process.returncode == 0:
            logger.warning(process)
        else:
            raise subprocess.SubprocessError(process.stderr)

    def __select_image(self):
        icon_map = {
            'clear-day': 'sunny_day.png',
            'clear-night': 'clear_night.png',
            'fog': 'fog.png',
            'partly-cloudy-day': 'partly_cloudy_day.png',
            'partly-cloudy-night': 'partly_cloudy_night.png',
            'cloudy': 'cloudy.png',
            'rain': 'rain_day.png',
            'thunderstorm': 'thunder_storms_day.png',
            'sleet': 'sleet.png',
            'snow': 'snow_night.png',
            'wind': 'wind.png',
        }
        missing_image = 'rainbow_other.png'
        display_image = icon_map.get(self.icon, missing_image)
        if display_image == missing_image:
            logger.error("image mapping doesn\'t exist for :\"" + str(self.icon) + "\" and a new image should be added to the existing map."
        return display_image

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

    def __display_data_failure(self, try_again_time):
        logger.warning('Displaying \"Failed / Try / Again on:\"')
        font = graphics.Font()
        font.LoadFont("/home/pi/projects/weather-python/rpi-rgb-led-matrix/fonts/5x7.bdf")
        textColor = graphics.Color(255,105,180)
        graphics.DrawText(self.matrix, font, 2, 10, textColor, "Failed")
        graphics.DrawText(self.matrix, font, 2, 20, textColor, "Try")
        graphics.DrawText(self.matrix, font, 2, 30, textColor, "Again on:")
        graphics.DrawText(
            self.matrix,
            font,
            2,
            40,
            textColor,
            try_again_time.strftime("%a")
        )
        graphics.DrawText(
            self.matrix,
            font,
            2,
            50,
            textColor,
            try_again_time.strftime("%H:%M")
        )

