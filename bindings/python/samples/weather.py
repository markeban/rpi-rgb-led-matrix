#!/usr/bin/env python
from samplebase import SampleBase
from rgbmatrix import graphics
import time
import pyowm


class GraphicsTest(SampleBase):
    def __init__(self, *args, **kwargs):
        super(GraphicsTest, self).__init__(*args, **kwargs)
        # self.canvas = self.matrix
        self.font = graphics.Font()
        self.font.LoadFont("../../../fonts/7x13.bdf")

    def run(self):
        self.__get_weather()
        self.__display_current()
        self.__display_todays_low()
        self.__display_todays_high()
        time.sleep(10)   # show display for 10 seconds before exit

    def __display_current(self):
        blue = graphics.Color(0, 0, 255)
        text = self.temp.get('temp') + ' \u00b0'
        graphics.DrawText(self.matrix, self.font, 2, 10, blue, text)

    def __display_todays_low(self):
        red = graphics.Color(0, 0, 255)
        text = self.temp.get('temp_min') + ' \u00b0'
        graphics.DrawText(self.matrix, self.font, 2, 10, red, text)

    def __display_todays_high(self):
        green = graphics.Color(0, 255, 0)
        text = self.temp.get('temp_max') + ' \u00b0'
        graphics.DrawText(self.matrix, self.font, 2, 10, green, text)

    def __get_weather(self):
        key = open(".env","r").read().rstrip('\n')
        owm = pyowm.OWM(key)
        observation = owm.weather_at_id(2643741) # Chicago
        self.temp = observation.get_weather().get_temperature('celsius')


# Main function
if __name__ == "__main__":
    graphics_test = GraphicsTest()
    if (not graphics_test.process()):
        graphics_test.print_help()
