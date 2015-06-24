# group_spotify

####_A way to tell what your friends are listening to_

The intent of this particular project is to provide a CLI application that will allow you to see what other people who are connected to the same server are listening to in Spotify.

Not gonna work in windows because ncurses doesn't work in windows, and I'm too lazy to figure out how to install Unicurses because it doesn't just work through pip. Should work _at minimum_ in OSX, and if I figure out how the hell to get the spotify currently playing track in Linux it'll work there too.

Initially written because I was informed that I had a day to do basically whatever at work then the idea kind of took off in my head at home before the actual day came.

Mostly I just wanted to play around with curses, redis, and websockets.

Much of the server code is almost directly cribbed from: https://gist.github.com/Lawouach/7698023

#Installation
###Client
Just run group_spotify.py
###Server
You'll need a redis instance.  Once you have that:
```
pip install redis-py
sudo pip3 install cherrypy
sudo pip3 install ws4py
```
Then run server.py

Server and client configs to probably come.  Probably.
