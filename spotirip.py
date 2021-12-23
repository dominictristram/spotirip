# spotirip.py - record a song on Spotify as a tagged mp3 on the local machine
#
# Initial version - Dominic Tristram 23/12/2021
#
# Requires the following to be installed on the Mac on which it runs:
#   Piezo - https://rogueamoeba.com/piezo/
#   Spotify
#   python > 3.5
#
# Usage:
#
# Record a given track by ID: python3 spotirip.py spotify:track:21cp8L9Pei4AgysZVihjSv
# Record the track currently playing: python3 spotirip.py
#
# Based on code by Bart Simons - https://bartsimons.me/ripping-spotify-songs-on-macos/
# I have made the following changes:
#   - if no command line parameter is given record the current song
#   - use the length of the track rather than checking on Spotify every half a second
#   - save by album artist rather than track artist so that compilations aren't broken
#   - add the track number to the filename
#   - use the user home directory environment variable rather than hard-coding it
#   - cleans-up after itself (close Piezo, pause Spotify)
#   - write track being ripped to the console
#   - generally improve efficiency and speed
#
import subprocess, sys, os, time, shutil, eyed3
from urllib.request import urlopen
from pathlib import Path

# Setup locations for files
home = str(Path.home())
piezoStorageLocation = home + '/Music/Piezo/'
ripStorageLocation   = home + '/Music/Ripped/'

# Clear all previous recordings if they exist
for f in os.listdir(piezoStorageLocation):
    os.remove(os.path.join(piezoStorageLocation,f))

# If we have been passed a track ID, play that. Otherwise use what is currently playing
if len(sys.argv) > 1:
	# Start playing the song to get the info
	subprocess.Popen('osascript -e "tell application \\"Spotify\\"" -e "play track \\"'+sys.argv[1]+'\\"" -e "end tell"', shell=True, stdout=subprocess.PIPE).stdout.read()
	trackid = sys.argv[1]
else:
	# See if we can get the Spotify track ID
	trackid  = subprocess.Popen('osascript -e "tell application \\"Spotify\\"" -e "current track\'s id" -e "end tell"', shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8').rstrip('\r\n')

# Get the artist name, track name, album name and album artwork URL from Spotify
albumartist  = subprocess.Popen('osascript -e "tell application \\"Spotify\\"" -e "current track\'s album artist" -e "end tell"', shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8').rstrip('\r\n')
artist  = subprocess.Popen('osascript -e "tell application \\"Spotify\\"" -e "current track\'s artist" -e "end tell"', shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8').rstrip('\r\n')
track   = subprocess.Popen('osascript -e "tell application \\"Spotify\\"" -e "current track\'s name" -e "end tell"', shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8').rstrip('\r\n')
album   = subprocess.Popen('osascript -e "tell application \\"Spotify\\"" -e "current track\'s album" -e "end tell"', shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8').rstrip('\r\n')
artwork = subprocess.Popen('osascript -e "tell application \\"Spotify\\"" -e "current track\'s artwork url" -e "end tell"', shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8').rstrip('\r\n')
duration = subprocess.Popen('osascript -e "tell application \\"Spotify\\"" -e "current track\'s duration" -e "end tell"', shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8').rstrip('\r\n')
tracknum = subprocess.Popen('osascript -e "tell application \\"Spotify\\"" -e "current track\'s track number" -e "end tell"', shell=True, stdout=subprocess.PIPE).stdout.read().decode('utf-8').rstrip('\r\n')

# Pause spotify
subprocess.Popen('osascript -e "tell application \\"Spotify\\" to pause"', shell=True, stdout=subprocess.PIPE).stdout.read()
time.sleep(.500)

print("TrackID: " + trackid)
print(albumartist + " " + album + " " + tracknum + " " + track)
intduration = int(duration)
actualdelay = (intduration / 1000)

# Download album artwork
artworkData = urlopen(artwork).read()

# Start recording. Start playing.
subprocess.Popen('osascript -e "activate application \\"Piezo\\"" -e "tell application \\"System Events\\"" -e "keystroke \\"r\\" using {command down}" -e "end tell"', shell=True, stdout=subprocess.PIPE).stdout.read()
subprocess.Popen('osascript -e "tell application \\"Spotify\\"" -e "play track \\"'+trackid+'\\"" -e "end tell"', shell=True, stdout=subprocess.PIPE).stdout.read()

# Wait for the length of the track
time.sleep(actualdelay)

# Stop the recording in Piezo
subprocess.Popen('osascript -e "activate application \\"Piezo\\"" -e "tell application \\"System Events\\"" -e "keystroke \\"r\\" using {command down}" -e "end tell"', shell=True, stdout=subprocess.PIPE).stdout.read()

# Pause Spotify
subprocess.Popen('osascript -e "tell application \\"Spotify\\" to pause"', shell=True, stdout=subprocess.PIPE).stdout.read()

# A little wait to give things the chance to finish
time.sleep(.500)

# Create directory for the album artist if it doesn't exist
if not os.path.exists(ripStorageLocation+albumartist):
    os.makedirs(ripStorageLocation+albumartist)

# Create directory for the album
if not os.path.exists(ripStorageLocation+albumartist+"/"+album):
    os.makedirs(ripStorageLocation+albumartist+"/"+album)

# Pad the track number with zeros
paddedtracknum = tracknum.zfill(2)

# Move MP3 file from Piezo folder to the folder containing rips.
for f in os.listdir(piezoStorageLocation):
        if f.endswith(".mp3"):
            shutil.move(piezoStorageLocation+f, ripStorageLocation+albumartist+"/"+album+"/"+paddedtracknum+" "+track+".mp3")

# Set and/or update ID3 information
musicFile = eyed3.load(ripStorageLocation+albumartist+"/"+album+"/"+paddedtracknum+" "+track+".mp3")
musicFile.tag.images.set(3, artworkData, "image/jpeg", trackid)
musicFile.tag.artist = artist
musicFile.tag.album  = album
musicFile.tag.title  = track
musicFile.tag.album_artist = albumartist

musicFile.tag.save()

# Quit Piezo
subprocess.Popen('osascript -e "activate application \\"Piezo\\"" -e "tell application \\"System Events\\"" -e "keystroke \\"q\\" using {command down}" -e "end tell"', shell=True, stdout=subprocess.PIPE).stdout.read()
