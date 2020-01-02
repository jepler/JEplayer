# JEplayer - MP3 Player for Adafruit PyGamer with CircuitPython

At this time, you need a special build of CircuitPython to get the latest MP3 playback goodies.  :frown: We're working to get this fixed ASAP!

Once that's dealt with, all you'll need to do is unzip the JEplayer distribution
to your PyGamer's CIRCUITPY drive, copy MP3 files to your MicroSD card, and pop
that in the PyGamer's slot.

## Device Orientation

Hold your PyGamer "vertically" with the stick at the bottom.

## Folders as playlists

JEplayer will show a list of all the top-level folders on the SD card.  Pick
one by moving the stick up and down, then press any button to start playing.
The files in it will be played in "naive sort" order.  If your files are named
like "01 - Track Name.mp3", this means the album will play in order.

To let JEplayer choose a folder at random, choose the top option.

## Album and Track Art

You can show artwork on the PyGamer's screen during playback.  If your playlist
is in the folder "They Might Be Giants - Flood", then in the root folder add a
128x128 or smaller uncompressed ".bmp"-format image called "They Might Be
Giants - Flood.bmp".  To make a special image for just one track, put it in the
album folder and name it the same as the track, such as "02 - Birdhouse In Your
Soul.bmp"

## Controls during playback

These controls will change soon, to an icon-driven system using the joystick.
For now, though, use these buttons to control playback:

 * A: Next Track
 * B: Previous Track
 * Start: Pause/Resume
 * Select: Choose Playlist

Whenever you go before the first track or after the last track, you'll be
returned to the album listing.

## VU Meter

The LEDs will pulse in time to the music.

## Headphones and Speakers

If headphones are plugged in to the jack on the PyGamer, the audio will come
out there.  Otherwise, you need a speaker plugged into the small connector on
the back labeled "Speaker".  Headphones with an in-line volume control are
best, because JEplayer can't control the playback volume itself.
