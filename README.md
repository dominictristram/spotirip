# spotirip
Record a track from Spotify as a tagged mp3 on a Mac.

Initial version by Dominic Tristram 23/12/2021

# Requirements
The following must be installed on the Mac on which it runs:
   - [Piezo](https://rogueamoeba.com/piezo/)
   - Spotify
   - python > 3.5

# Usage:

Record a given track by ID - supply ID on command line, eg:
`python3 spotirip.py spotify:track:21cp8L9Pei4AgysZVihjSv`

Record the track currently playing - no command line parameter, eg:
`python3 spotirip.py`

Based on [code by Bart Simons](https://bartsimons.me/ripping-spotify-songs-on-macos/)

I have made the following changes:
   - if no command line parameter is given record the current song
   - use the length of the track rather than checking on Spotify every half a second
   - save by album artist rather than track artist so that compilations aren't broken
   - add the track number to the filename
   - use the user home directory environment variable rather than hard-coding it
   - cleans-up after itself (close Piezo, pause Spotify)
   - write track being ripped to the console
   - generally improve efficiency and speed
 
Note that this code is for interest/research only. I do not condone unauthorised use of Spotify content.
