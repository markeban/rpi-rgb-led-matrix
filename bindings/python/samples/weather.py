#!/usr/bin/env python
from samplebase import SampleBase
from rgbmatrix import graphics
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image
import pyowm
import time
import sys


MAX_TRIES_API_CALL = 6

class GraphicsTest(SampleBase):
    def __init__(self, *args, **kwargs):
        super(GraphicsTest, self).__init__(*args, **kwargs)
        self.api_tries = 0

    def run(self):
        while True:
            self.__get_weather()
            self.__display_current()
            self.__display_image()
            self.__display_todays_low()
            self.__display_todays_high()
            time.sleep(600) # show display for 10 minutes before refreshing
            self.matrix.Clear()

    def __display_current(self):
        font = graphics.Font()
        font.LoadFont("../../../fonts/7x13.bdf")
        blue = graphics.Color(0, 0, 255)
        temp_string = str(round(self.temp.get('temp')))
        text = temp_string + '\u00b0C'
        graphics.DrawText(self.matrix, font, 2, 10, blue, text)

    def __display_image(self):
        image = Image.open('snow_clouds.png')
        self.matrix.SetImage(image.convert('RGB'), 0, 10)

    def __display_todays_low(self):
        font = graphics.Font()
        font.LoadFont("../../../fonts/5x7.bdf")
        red = graphics.Color(0, 0, 255)
        temp_min_string = str(round(self.temp.get('temp_min')))
        text = '\u2193 ' +  temp_min_string + '\u00b0C'
        graphics.DrawText(self.matrix, font, 2, 52, red, text)

    def __display_todays_high(self):
        font = graphics.Font()
        font.LoadFont("../../../fonts/5x7.bdf")
        green = graphics.Color(0, 255, 0)
        temp_max_string = str(round(self.temp.get('temp_max')))
        text = '\u2191 ' + temp_max_string + '\u00b0C'
        graphics.DrawText(self.matrix, font, 2, 62, green, text)

    def __get_weather(self):
        key_file = open(".env", "r")
        key = key_file.read().rstrip('\n')
        try:
            owm = pyowm.OWM(key)
            observation = owm.weather_at_id(4887398)  # Chicago
            new_temp = observation.get_weather().get_temperature('celsius')
        except (pyowm.exceptions.api_response_error.APIResponseError, pyowm.exceptions.api_call_error.APICallTimeoutError) as error:
            print(error)
            self.api_tries += 1
            if self.api_tries >= MAX_TRIES_API_CALL:
                raise "API call failed 6 times in a row. Will not try again"
            else:
                print("Will try again in 10 minutes to update weather data. Displaying old data.")
                pass
        else:
            self.api_tries = 0
            self.temp = new_temp
        finally:
            key_file.close()

# Main function
if __name__ == "__main__":
    graphics_test = GraphicsTest()
    if (not graphics_test.process()):
        graphics_test.print_help()
