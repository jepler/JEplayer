import adafruit_imageload.bmp
import board
import displayio

def make_palette(seq):
    """Create a palette from a sequence of colors"""
    p = displayio.Palette(len(seq))
    for i, si in enumerate(seq):
        if si is None:
            p.make_transparent(i)
        else:
            p[i] = si
    return p
 
BLACK, WHITE, RED, BLUE = 0x111111, 0xffffff, 0xff0000, 0x0000ff

palette_normal    = make_palette([BLACK, WHITE, BLACK, BLACK])
palette_selected  = make_palette([BLACK, WHITE, RED, BLACK])
palette_active    = make_palette([BLACK, WHITE, BLACK, BLUE])
palette_both      = make_palette([BLACK, WHITE, RED, BLUE])
palettes = [palette_normal, palette_active, palette_selected, palette_both]

class IconBar:
    """An icon bar presents n 16x16 icons in a row.  One icon can be "selected" and any number can be "active"."""
    def __init__(self, n=8, filename="/rsrc/icons.bmp"):
        self.group = displayio.Group(max_size=n)
        self.bitmap_file = open(filename, "rb")
        self.bitmap = adafruit_imageload.bmp.load(self.bitmap_file, bitmap=displayio.Bitmap)[0]

    
        self._selected = None
        self.icons = [displayio.TileGrid(self.bitmap,
                                         pixel_shader=palette_normal, x=16*i,
                                         y=0, width=1, height=1,
                                         tile_width=16, tile_height=16)
                      for i in range(n)]
        self.active = [False] * n

        for i, icon in enumerate(self.icons):
            icon[0] = i
            self.group.append(icon)
        self.select(0)

    @property
    def selected(self):
        """The currently selected icon"""
        return self._selected

    @selected.setter
    def selected(self, n):
        select(n)

    def select(self, n):
        old_selected = self._selected
        self._selected = n
        if n != old_selected:
            self._refresh(n)
            if old_selected is not None:
                self._refresh(old_selected)

    def set_active(self, n, new_state):
        """Sets the n'th icon's active state to new_state"""
        new_state = bool(new_state)
        if self.active[n] == new_state:
            return
        self.active[n] = new_state
        self._refresh(n)

    def activate(self, n):
        """Set the n'th icon to be active"""
        self.set_active(n, True)

    def deactivate(self, n):
        """Set the n'th icon to be inactive"""
        self.set_active(n, False)

    def toggle(self, n):
        """Toggle the state of the n'th icon"""
        self.set_active(n, not self.active[n])
        print()

    def _refresh(self, n):
        """Update the appearance of the n'th icon"""
        palette_index = self.active[n] + 2 * (self._selected == n)
        self.icons[n].pixel_shader = palettes[palette_index]
