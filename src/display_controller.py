
import time
import sys
import os
import logging
import random
import datetime

from PIL import Image, ImageDraw, ImageFont
from rgbmatrix import RGBMatrix, RGBMatrixOptions


class DisplayController(object):
    """Module for controlling the display"""

    def __init__(self):
        """Instantiate the object"""
        logging.getLogger().setLevel(logging.DEBUG)
        self._configure_options()
        self.matrix = RGBMatrix(options=self.options)
        self.available_gifs = self._get_all_gifs()

    def _get_all_gifs(self):
        """Returns a list of all gifs in the image dir"""
        image_dir = self._get_image_dir()
        return [x for x in os.listdir(image_dir) if x.endswith('.gif')]

    def _get_default_font(self, size=24):
        """Returns the default font"""
        return ImageFont.truetype("fonts/Roboto-Medium.ttf", size)

    def _configure_options(self):
        """Configures display options"""
        self.options = RGBMatrixOptions()
        self.options.rows = 64
        self.options.cols = 64
        self.options.chain_length = 1
        self.options.row_address_type = 0
        self.options.parallel = 1
        self.options.multiplexing = 0
        self.options.pwm_bits = 11
        self.options.brightness = 100
        self.options.pwm_lsb_nanoseconds = 130
        self.options.led_rgb_sequence = "RGB"
        self.options.pixel_mapper_config = ""
        self.options.panel_type = ""

    def pulse_colours(self):
        """Pulses colours"""
        logging.info('Pulsing colours')
        self.offscreen_canvas = self.matrix.CreateFrameCanvas()
        continuum = 0
        while True:
            self._usleep(5 * 1000)
            continuum += 1
            continuum %= 3 * 255
            red = 0
            green = 0
            blue = 0
            if continuum <= 255:
                c = continuum
                blue = 255 - c
                red = c
            elif continuum > 255 and continuum <= 511:
                c = continuum - 256
                red = 255 - c
                green = c
            else:
                c = continuum - 512
                green = 255 - c
                blue = c
            self.offscreen_canvas.Fill(red, green, blue)
            self.offscreen_canvas = self.matrix.SwapOnVSync(self.offscreen_canvas)

    def _usleep(self, value):
        """Sleep x microseconds"""
        time.sleep(value / 1000000.0)

    def _get_image_dir(self):
        """Returns the image dir"""
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'images')

    def _get_image_file(self, file_name):
        """Returns the full path to the image file"""
        image_dir = self._get_image_dir()
        return os.path.join(image_dir, file_name)

    def _display_still(self, image, seconds=3):
        """Displays a still image"""
        logging.debug('Displaying still')
        image.thumbnail((self.matrix.width, self.matrix.height), Image.ANTIALIAS)
        self.matrix.SetImage(image.convert('RGB'))
        time.sleep(seconds)
    
    def _get_blank_image(self):
        """Returns a blank image"""
        return Image.new(mode="RGB", size=(self.matrix.width, self.matrix.height))
    
    def _display_black_image(self):
        """Displays a black image"""
        image = self._get_blank_image()
        self.matrix.SetImage(image.convert('RGB'))

    def _display_animated_gif(self, image):
        """Displays a gif on the display"""
        logging.debug('Displaying GIF')
        for frame in range(0, image.n_frames):
            image.seek(frame)
            throwaway_image = image.copy()
            throwaway_image.thumbnail((self.matrix.width, self.matrix.height), Image.ANTIALIAS)
            self.matrix.SetImage(throwaway_image.convert('RGB'))
            frame_dir = int(image.info['duration']) / 1000
            # frame_dir = 0.5
            time.sleep(frame_dir)

    def display_image(self, image_filepath, seconds=3):
        """Displays an image on the display"""
        self._display_black_image()
        logging.info(f'Displaying image: {image_filepath}')
        image = Image.open(image_filepath)
        if hasattr(image, 'is_animated'):
            self._display_animated_gif(image)
        else:
            self._display_still(image, seconds=seconds)

    def display_random_gif(self):
        """Displays a random gif"""
        self.display_image(self._get_image_file(random.choice(self.available_gifs)))

    def _calculate_days_to_xmas(self):
        """Calculates the number of days until next xmas"""
        now = datetime.datetime.now()
        year = now.year
        if now > datetime.datetime(year=year, month=12, day=25):
            # Account for the days after xmas of the remaining year
            year = year + 1
        delta = now - datetime.datetime(year=year, month=12, day=25)
        return abs(int(delta.days))

    def _display_text(self, text, font_size=32):
        """Puts text on the display"""
        image = self._get_blank_image()
        draw = ImageDraw.Draw(image)
        font = self._get_default_font(font_size)
        tw, th = draw.textsize(text, font=font)
        position_x = (self.matrix.width - tw) / 2
        position_y = (self.matrix.height - th) / 2
        draw.text((position_x, position_y), text, font=font)
        self.matrix.SetImage(image.convert('RGB'))

    def display_days_until_xmas(self, duration=120):
        """Displays the number of days until xmas"""
        days_until = self._calculate_days_to_xmas()
        prefix_words = ['DAYS', 'UNTIL', 'XMAS']
        for word in prefix_words:
            self._display_text(word, 16)
            time.sleep(0.8)
        self._display_text(str(days_until))
        time.sleep(duration)

    def run(self):
        logging.info('Starting application')
        try:
            while True:
                self._display_black_image()
                self.display_days_until_xmas()
                self.display_random_gif()
        except KeyboardInterrupt:
            pass


if __name__ == '__main__':
    dc = DisplayController()
    dc.run()
