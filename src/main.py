import adafruit_bitmap_font.bitmap_font
import adafruit_display_text.label
import bar
import adafruit_sdcard
import analogjoy
import analogio
import audiocore
import audioio
import audiomp3
import board
import busio
import digitalio
import displayio
import gamepadshift
import gc
import microcontroller
import neopixel
import os
import random
import repeat
import storage
import terminalio
import time

def clear_display():
    board.DISPLAY.show(displayio.Group(max_size=1))

board.DISPLAY.rotation = 0
clear_display()

def px(x, y):
    return 0 if x <= 0 else round(x / y)

class PlaybackDisplay:
    def __init__(self):
        self.group = displayio.Group(max_size=4)
        self.glyph_width, self.glyph_height = font.get_bounding_box()[:2]
        self.pbar = bar.Bar(0, 0, board.DISPLAY.width,
                self.glyph_height, colors=(0x0000ff, None))
        self.label = adafruit_display_text.label.Label(font, line_spacing=1.0,
                max_glyphs=256)
        self.label.y = 6
        self._bitmap_filename = None
        self._fallback_bitmap = ["/rsrc/background.bmp"]
        self.set_bitmap([])
        self.group.append(self.pbar)
        self.group.append(self.label)
        self.pixels = neopixel.NeoPixel(board.NEOPIXEL, 5)
        self.pixels.auto_write = False
        self.pixels.fill(0)
        self.pixels.show()

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, text):
        if len(text) > 256: text = text[:256]
        self._text = text
        self.label.text = text

    @property
    def progress(self):
        return self.pbar.value

    @progress.setter
    def progress(self, frac):
        self.pbar.value = frac

    def set_bitmap(self, candidates):
        for c in candidates + self._fallback_bitmap:
            if c == self._bitmap_filename:
                return # Already loaded
            try:
                f = _bitmap_file = open(c, 'rb')
            except OSError as e:
                continue
            bitmap = displayio.OnDiskBitmap(f)
            self._bitmap_filename = c
            # Create a TileGrid to hold the bitmap
            self.tile_grid = displayio.TileGrid(bitmap,
                    pixel_shader=displayio.ColorConverter())

            # Add the TileGrid to the Group
            if len(self.group) == 0:
                self.group.append(self.tile_grid)
            else:
                self.group[0] = self.tile_grid
            self.tile_grid.x = 0
            self.tile_grid.y = self.glyph_height*2
            break

    @property
    def rms(self):
        return self._rms

    @rms.setter
    def rms(self, value):
        self._rms = value
        self.pixels[0] = (20, 0, 0) if value > 20 else (px(value, 1), 0, 0)
        self.pixels[1] = (20, 0, 0) if value > 40 else (px(value - 20, 1), 0, 0)
        self.pixels[2] = (20, 0, 0) if value > 80 else (px(value - 40, 2), 0, 0)
        self.pixels[3] = (20, 0, 0) if value > 160 else (px(value - 80, 4), 0, 0)
        self.pixels[4] = (20, 0, 0) if value > 320 else (px(value - 160, 8), 0, 0)
        self.pixels.show()

enable = digitalio.DigitalInOut(board.SPEAKER_ENABLE)
enable.direction = digitalio.Direction.OUTPUT
enable.value = True
speaker = audioio.AudioOut(board.SPEAKER, right_channel=board.A1)
mp3stream = audiomp3.MP3File(open("/rsrc/splash.mp3", "rb"))
speaker.play(mp3stream)

font = adafruit_bitmap_font.bitmap_font.load_font("rsrc/5x8.bdf")
playback_display = PlaybackDisplay()
board.DISPLAY.show(playback_display.group)
font.load_glyphs(range(32, 128))

def change_stream(filename):
    old_stream = mp3stream.file
    mp3stream.file = open(filename, "rb")
    old_stream.close()
    return mp3stream.file

adc_vbat = analogio.AnalogIn(board.A6)
scale_vbat = 2 * adc_vbat.reference_voltage / 65535

BUTTON_SEL = const(8)
BUTTON_START = const(4)
BUTTON_A = const(2)
BUTTON_B = const(1)


joystick = analogjoy.AnalogJoystick()

if board.DISPLAY.rotation == 270:
    up_key = repeat.KeyRepeat(lambda: joystick.up, rate=0.2)
    down_key = repeat.KeyRepeat(lambda: joystick.down, rate=0.2)
    left_key = repeat.KeyRepeat(lambda: joystick.left, rate=0.2)
    right_key = repeat.KeyRepeat(lambda: joystick.right, rate=0.2)
else:
    left_key = repeat.KeyRepeat(lambda: joystick.up, rate=0.2)
    right_key = repeat.KeyRepeat(lambda: joystick.down, rate=0.2)
    down_key = repeat.KeyRepeat(lambda: joystick.left, rate=0.2)
    up_key = repeat.KeyRepeat(lambda: joystick.right, rate=0.2)

buttons = gamepadshift.GamePadShift(digitalio.DigitalInOut(board.BUTTON_CLOCK),
                                    digitalio.DigitalInOut(board.BUTTON_OUT),
                                    digitalio.DigitalInOut(board.BUTTON_LATCH))

def mount_sd():
    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
    cs = digitalio.DigitalInOut(board.SD_CS)
    sdcard = adafruit_sdcard.SDCard(spi, cs)
    vfs = storage.VfsFat(sdcard)
    storage.mount(vfs, "/sd")

def join(base, *args):
    for a in args: base = base + '/' + a
    return base

def play_all(dir='/sd'):
    with digitalio.DigitalInOut(board.SPEAKER_ENABLE) as enable:
        enable.direction = digitalio.Direction.OUTPUT
        enable.value = True
        # In 5.0a1, stereo playback on samd dac doesn't work due to a bug
        #with audioio.AudioOut(board.SPEAKER, right_channel=board.A1) as speaker:
        with audioio.AudioOut(board.SPEAKER) as speaker:
            for f in os.listdir(dir):
                if f.lower().endswith('.mp3'):
                    play_one_file(speaker, join(dir, f))

def blank_screen():
    displayio.release_displays()

# https://en.wikipedia.org/wiki/Fisher%E2%80%93Yates_shuffle#The_modern_algorithm
def shuffle(seq):
    for i in range(len(seq)-2):
        j = random.randint(i, len(seq)-1)
        seq[i], seq[j] = seq[j], seq[i]

def menu_choice(seq, button_ok, button_cancel, *, sel_idx=0, font=font):
    board.DISPLAY.auto_refresh = True
    scroll_idx = sel_idx
    glyph_width, glyph_height = font.get_bounding_box()[:2]
    num_rows = min(len(seq), board.DISPLAY.height // glyph_height)
    max_glyphs = board.DISPLAY.width // glyph_width
    labels = [adafruit_display_text.label.Label(font, max_glyphs=max_glyphs)
                for i in range(num_rows)]
    cursor = adafruit_display_text.label.Label(font, max_glyphs=1, color=0xddddff)
    y0 = (glyph_height+1)//2
    scene = displayio.Group(max_size=len(labels) + 1)
    for i, li in enumerate(labels):
        li.x = round(glyph_width * 1.5)
        li.y = y0 + glyph_height * i
        li.text = seq[i][:max_glyphs]
        scene.append(li)
    cursor.x = 0 
    cursor.y = y0
    cursor.text = ">"
    scene.append(cursor)

    last_scroll_idx = max(0, len(seq) - num_rows - 1)

    board.DISPLAY.show(scene)
    buttons.get_pressed() # Clear out anything from before now
    i = 0
    while True:
        enable.value = speaker.playing
        pressed = buttons.get_pressed()
        if button_cancel and (pressed & button_cancel): return -1
        if pressed & button_ok: return sel_idx

        joystick.poll()
        if up_key.value: sel_idx -= 1
        if down_key.value: sel_idx += 1

        sel_idx = min(len(seq)-1, max(0, sel_idx))

        if scroll_idx > sel_idx or scroll_idx + num_rows <= sel_idx:
            scroll_idx = sel_idx - num_rows // 2
        scroll_idx = min(last_scroll_idx, max(0, scroll_idx))

        for i in range(scroll_idx, scroll_idx + num_rows):
            j = i - scroll_idx
            new_text = ''
            if i < len(seq):
                new_text = seq[i][:max_glyphs]
            if new_text != labels[j].text:
                labels[j].text = new_text

        cursor.y = y0 + glyph_height * (sel_idx - scroll_idx)

        time.sleep(1/20)

S_IFDIR = const(16384)
def isdir(x): return os.stat(x)[0] & S_IFDIR
def choose_folder(base='/sd'):
    all_folders = sorted(m for m in os.listdir(base) if isdir(join(base, m)))
    choices = ['Surprise Me'] + all_folders

    idx = menu_choice(choices,
            BUTTON_START | BUTTON_A | BUTTON_B | BUTTON_SEL, 0)
    clear_display()
    if idx >= 1: result = all_folders[idx-1]
    else: result = random.choice(all_folders)
    return join(base, result)

def wait_no_button_pressed():
    while buttons.get_pressed(): time.sleep(1/20)

def average_temperature(n=20):
    return sum(microcontroller.cpu.temperature for i in range(n)) / n

_bitmap_file = None
def play_one_file(speaker, idx, filename, folder, title, next_title):
    board.DISPLAY.auto_refresh = False

    playback_display.set_bitmap([
            filename.rsplit('.', 1)[0] + ".bmp",
            filename.rsplit('/', 1)[0] + ".bmp"])

    playback_display.text = "%s\n%s" % (folder, title)

    board.DISPLAY.refresh()

    result = idx + 1
    wait_no_button_pressed()
    paused = False
    sz = os.stat(filename)[6]
    f = change_stream(filename)
    speaker.play(mp3stream)
    board.DISPLAY.auto_refresh = True
    while speaker.playing:

        gc.collect()

        playback_display.rms = mp3stream.rms_level
        playback_display.progress = f.tell() / sz

        pressed = buttons.get_pressed()
        # SEL: cancel playlist
        if pressed & BUTTON_SEL:
            result = -1
            break
        # START: play/pause
        if pressed & BUTTON_START:
            wait_no_button_pressed()
            if paused:
                speaker.resume()
                paused = False
            else:
                playback_display.rms = 0
                speaker.pause()
                paused = True
            wait_no_button_pressed()
        # A: previous track
        if pressed & BUTTON_B:
            result = idx - 1
            break
        # B: next track
        if pressed & BUTTON_A:
            result = idx + 1
            break
            
    speaker.stop()
    playback_display.rms = 0
 
    gc.collect()

    return result

def play_all(playlist, *, folder='', trim=0, dir='/sd'):
    i = 0
    board.DISPLAY.show(playback_display.group)
    while i >= 0 and i < len(playlist):
        f = playlist[i]
        next_up = (playlist[i+1][trim:-4]
                    if i+1 < len(playlist) else "(the end)")
        i = play_one_file(speaker, i, join(dir, f), folder, f[trim:-4], next_up)
    speaker.stop()
    clear_display()
    
def longest_common_prefix(seq):
    seq0 = seq[0]
    for i in range(0, len(seq0)):
        for j in seq:
            if len(j) < i or j[i] != seq0[i]: return i
    return len(seq0)

def play_folder(dir):
    playlist = [d for d in os.listdir(dir) if d.lower().endswith('.mp3')]
    if not playlist:
        # hmm, no mp3s in a folder?  Well, don't crash okay?
        del playlist
        gc.collect()
        return
    playlist.sort()
    trim = longest_common_prefix(playlist)
    enable.value = True
    play_all(playlist, folder=dir.split('/')[-1], trim=trim, dir=dir)
    enable.value = False

try:
    mount_sd()
except OSError as detail:
    t = adafruit_display_text.label.Label(font,
        text="%s\n\nInsert or re-seat\nSD card\nthen press reset"
            % detail.args[0])
    t.x = 8
    t.y = board.DISPLAY.height // 2
    g = displayio.Group()
    g.append(t)
    board.DISPLAY.show(g)
    while True:
        time.sleep(1)

while True:
    folder = choose_folder()
    play_folder(folder)

