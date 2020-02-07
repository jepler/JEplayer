# JEplayer - MP3 Player for Adafruit PyGamer with CircuitPython

Make sure you are using CircuitPython 5.0.0.beta6 or newer for JEplayer.
(If beta6 is not out yet, that means use the latest build from the master
branch)

Once that's dealt with, all you'll need to do is unzip the JEplayer distribution
to your PyGamer's CIRCUITPY drive, copy MP3 files to your MicroSD card using a USB adapter,
and pop that in the PyGamer's slot.

## Device Orientation

Hold your PyGamer "vertically" with the stick at the bottom.

## Choosing MP3s

JEplayer works best with 128kBit/s MP3 files with a sample rate of 44.1kHz.
 
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

During playback, control JEplayer via the icon bar at the bottom of the screen.
Press left and right on the stick select an icon -- the current one is outlined
with a red square -- and then press any button to invoke the desired icon.

Some buttons can be "active", in which case the background is blue.

From left to right:
 * Play: Play or pause the current track.  Active to show the track is currently playing.
 * Pause: Play or pause the current track.  Active to show the track is currently paused.
 * Stop: Return to the folder listing
 * Previous Track: Go to the previous track (or a random track, if shuffle is on)
 * Next Track: Go to the next track (or a random track, if shuffle is on)
 * Repeat: Switch repeat mode on or off.  When active, after the last track in the folder, play continues with the first track.  Mutually exclusive with Shuffle and All Folders
 * Shuffle: Switch shuffle mode on or off.  When active, after each track, select a different random track from the folder.  Mutually exclusive with Repeat and All Folders
 * All Folders: Switch all folders on or off.  When active, after the last track in the folder, play continues with the next folder.  Mutually exclusive with Shuffle and Repeat

## VU Meter

The LEDs will pulse in time to the music.

## Headphones and Speakers

If headphones are plugged in to the jack on the PyGamer, the audio will come
out there.  Otherwise, you need a speaker plugged into the small connector on
the back labeled "Speaker".  Headphones with an in-line volume control are
best, because JEplayer can't control the playback volume itself.
