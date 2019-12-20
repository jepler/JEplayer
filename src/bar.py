import displayio

class Bar(displayio.TileGrid):
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
        for i in range(0, height*2, 2): self._bitmap[i] = 1

        super().__init__(self._bitmap, pixel_shader=self._palette, x=x, y=y, width=width, tile_width=1)

        self.value = value
    
    @property
    def value(self):
        return self._value

    @value.setter
    def value(self, newvalue):
        self._value = newvalue
        j = newvalue * self._width - .5
        for i in range(self._width):
            self[i] = i <= j
    
