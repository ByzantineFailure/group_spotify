# group_spotify

####_A way to tell what your friends are listening to_

The intent of this particular project is to provide a CLI application that will allow you to see what other people who are connected to the same server are listening to in Spotify.

Not gonna work in windows because ncurses doesn't work in windows, and I'm too lazy to figure out how to install Unicurses because it doesn't just work through pip. Should work _at minimum_ in OSX, and if I figure out how the hell to get the spotify currently playing track in Linux it'll work there too.

Initially written because I was informed that I had a day to do basically whatever at work then the idea kind of took off in my head at home before the actual day came.

Mostly I just wanted to play around with curses, redis, and websockets.  Redis didn't happen (unneded).

#Installation
###Client
```
pip3 install websocket-client
```
Then run group_spotify.py

###Server
```
pip3 install tornado
```
Then run server.py

#TODO
Clean the code up.  That shit is a hot mess right now.

Server and client configs

Some sort of tests or something

Linux method of getting Spotify info

Stabilize the network stuff to not fail in the event of the connection going down

Stabilize the WindowsSpotifyScraper for the event of Spotify not being present

Port the UI to Unicurses so it works under Windows as well

Deploy this somewhere or something
