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
import os
import random
import repeat
import storage
import terminalio
import time

adc_vbat = analogio.AnalogIn(board.A6)
scale_vbat = 2 * adc_vbat.reference_voltage / 65535

BUTTON_SEL = const(8)
BUTTON_START = const(4)
BUTTON_A = const(2)
BUTTON_B = const(1)

joystick = analogjoy.AnalogJoystick()
up_key = repeat.KeyRepeat(lambda: joystick.up, rate=0.2)
down_key = repeat.KeyRepeat(lambda: joystick.down, rate=0.2)
left_key = repeat.KeyRepeat(lambda: joystick.left, rate=0.2)
right_key = repeat.KeyRepeat(lambda: joystick.right, rate=0.2)

buttons = gamepadshift.GamePadShift(digitalio.DigitalInOut(board.BUTTON_CLOCK),
                                    digitalio.DigitalInOut(board.BUTTON_OUT),
                                    digitalio.DigitalInOut(board.BUTTON_LATCH))

def mount_sd():
    spi = busio.SPI(board.SCK, MOSI=board.MOSI, MISO=board.MISO)
    cs = digitalio.DigitalInOut(board.SD_CS)
    sdcard = adafruit_sdcard.SDCard(spi, cs)
    vfs = storage.VfsFat(sdcard)
    storage.mount(vfs, "/sd")

def play_one_file(speaker, filename):
    with open(filename, "rb") as f, audiomp3.MP3File(f) as mp3:
        speaker.play(mp3)
        while speaker.playing:
            time.sleep(.1)

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

def clear_display():
    board.DISPLAY.show(displayio.Group(max_size=1))

def menu_choice(seq, button_ok, button_cancel, *, sel_idx=0, font=terminalio.FONT):
    scroll_idx = sel_idx
    glyph_width, glyph_height = font.get_bounding_box()
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

def choose_mp3s():
    all_mp3s = sorted(m for m in os.listdir('/sd') if m.lower().endswith(".mp3"))
    choices = (['Play All', 'Shuffle All'] +
        [i[:-4].replace("_", " ") for i in all_mp3s])

    idx = menu_choice(choices, BUTTON_START | BUTTON_A | BUTTON_B, BUTTON_SEL)
    if idx < 0: return []
    if idx > 2: return [all_mp3s[idx-2]]
    if idx == 1: shuffle(all_mp3s)
    return all_mp3s

def wait_no_button_pressed():
    while buttons.get_pressed(): time.sleep(1/20)

def average_temperature(n=20):
    return sum(microcontroller.cpu.temperature for i in range(n)) / n

def play_one_file(speaker, idx, filename, title, next_title):
    font = terminalio.FONT
    glyph_width, glyph_height = font.get_bounding_box()

    scene = displayio.Group(max_size=3)

    text = adafruit_display_text.label.Label(font, text=
        "  Now playing:\n%s\n\n  Next up:\n%s" % (title, next_title))
    text.x = 0
    text.y = board.DISPLAY.height//2
    scene.append(text)

    info = adafruit_display_text.label.Label(terminalio.FONT, max_glyphs=32)
    info.x = 0
    info.y = board.DISPLAY.height - glyph_height // 2
    scene.append(info)

    progress = bar.Bar(0, 0, board.DISPLAY.width, glyph_height, colors=(0x0000ff, None))
    scene.append(progress)

    board.DISPLAY.show(scene)

    result = idx + 1
    wait_no_button_pressed()
    paused = False
    sz = os.stat(filename)[6]
    with open(filename, "rb") as f, audiomp3.MP3File(f) as mp3:
        speaker.play(mp3)
        while speaker.playing:

            gc.collect()
            free = gc.mem_free()
            vbat = adc_vbat.value * scale_vbat
            temp = average_temperature()
            info.text = ("%6db    %3.1fv    % 2.0fC" % (free, vbat, temp))[:32]

            progress.value = f.tell() / sz

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
                
            time.sleep(1/15)
    clear_display()
    return result

def play_all(playlist, *, dir='/sd'):
    # In 5.0a1, stereo playback on samd dac doesn't work due to a bug
    # This will be fixed in the next release, but for now you can
    # uncomment the next line and delete the one after it
    #with audioio.AudioOut(board.SPEAKER) as speaker, \
    with audioio.AudioOut(board.SPEAKER, right_channel=board.A1) as speaker, \
            digitalio.DigitalInOut(board.SPEAKER_ENABLE) as enable:
        enable.direction = digitalio.Direction.OUTPUT
        enable.value = True
        i = 0
        while i >= 0 and i < len(playlist):
            f = playlist[i]
            next_up = playlist[i+1][:-4] if i+1 < len(playlist) else "(the end)"
            i = play_one_file(speaker, i, join(dir, f), f[:-4], next_up)
        speaker.stop()

mount_sd()
while True:
    playlist = choose_mp3s()
    clear_display()
    play_all(playlist)

