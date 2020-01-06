# The MIT License (MIT)
#
# Copyright (c) 2020 Jeff Epler for Adafruit Industries LLC
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
"""
Display a Progress Bar
"""

import displayio

class Bar(displayio.TileGrid):
    """Progress Bar"""
    def __init__(self, x, y, width, height, *, value=0, colors=[0xffffff, None]):
        self._palette = displayio.Palette(2)
        for i in range(2):
            if colors[i] is None:
                self._palette.make_transparent(i)
            else:
                self._palette[i] = colors[i]

        self._width = width
        self._height = height
        self._bitmap = displayio.Bitmap(2, height, 2)
        for i in range(0, height*2, 2):
            self._bitmap[i] = 1

        super().__init__(self._bitmap, pixel_shader=self._palette, x=x, y=y,
                         width=width, tile_width=1)

        self.value = value

    @property
    def value(self):
        """The current value of the progress bar, from 0 to 1"""
        return self._value

    @value.setter
    def value(self, newvalue):
        self._value = newvalue
        j = newvalue * self._width - .5
        for i in range(self._width):
            self[i] = i <= j
