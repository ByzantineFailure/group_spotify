import threading
import sys
import subprocess
import time
from os.path import expanduser
from common import User

class SpotifyWatcher(threading.Thread):
    def __init__(self, state, data_sender):
        current_os = sys.platform
        self.state = state
        self.data_sender = data_sender
        self.homedir = expanduser("~")
        self.valid_os = "darwin" in current_os
        if not self.valid_os:
            self.state.add_log_message("Not running on a supported OS!  Cannot detect spotify song.")
        
        threading.Thread.__init__(self)

    def run(self):
        if not self.valid_os:
            return

        while True:
            subprocess.call(["./getSpotifySong.as",""])
            
            f = open(self.homedir + '/nowplaying.txt', 'r')
            song = f.readline()[:-1]
            artist = f.readline()[:-1]
            playing = f.readline() == "playing"
            
            user_update = User(self.state.current_user_name, song, artist, playing)
            
            if song != self.state.current_user_song or artist != self.state.current_user_artist or playing != self.state.current_user_playing:
                self.data_sender.update_user(user_update)      

            self.state.lock.acquire()
            self.state.update_current_user_values(user_update)
            self.state.lock.release()
            
            time.sleep(1)

if __name__ == "__main__":
    class DummyState:
        def __init__(self):
            self.current_user_name = "Mike"
            self.lock = DummyLock()
            print("Starting watcher test")
        
        def add_log_message(self, message):
            print(message)

        def update_current_user(self, user):
            print("Updating user to listening to {} - {}".format(user.song, user.artist))

    class DummyLock:
        def __init__(self):
            print("Initting dummy lock")
        def acquire(self):
            print("Acquiring dummy lock")
        def release(self):
            print("Releasing dummy lock")

    state = DummyState()
    watcher = SpotifyWatcher(state)
    watcher.start()
