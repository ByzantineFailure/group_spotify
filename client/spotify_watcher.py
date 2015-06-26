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
            self.scraper = DummyScraper(self.state.current_user_name)
        else:
            self.scraper = AppleSpotifyScraper(self.state.current_user_name)
        
        threading.Thread.__init__(self)

    def run(self):
        if not self.valid_os:
            return

        while True:
            user_update = self.scraper.scrape()
            
            if user_update.song != self.state.current_user_song or user_update.artist != self.state.current_user_artist or user_update.playing != self.state.current_user_playing:
                self.data_sender.update_user(user_update)      

            self.state.lock.acquire()
            self.state.update_current_user_values(user_update)
            self.state.lock.release()
            
            time.sleep(1)

class AppleSpotifyScraper:
    def __init__(self, user_name):
        print("Apple Spotify scraper created")
        self.user_name = user_name

    def scrape(self):
       script = """
           tell application "Spotify"
                set theTrack to current track
                set theArtist to artist of theTrack
                set theName to name of theTrack
                    if player state is playing then
                    set playStatus to "playing"
                else
                    set playStatus to "notPlaying"
                end if
            end tell
            set theValue to theName & "\n" & theArtist & "\n" & playStatus
            return theValue
       """.encode('UTF-8')
       osa = subprocess.Popen(['osascript', '-'], stdin=subprocess.PIPE, stdout=subprocess.PIPE)
       result = osa.communicate(script)[0].decode("UTF-8").split("\n");
       return User(self.user_name, result[0], result[1], result[2]=="playing")

class DummyScraper:
    def __init__(self, user_name):
        self.user_name = user_name
        print("Dummy Spotify scraper created")

    def scrape(self):
        return User(self.user_name, "UNKNOWN", "UNKNOWN", "UNKNOWN")

if __name__ == "__main__":
    class DummyState:
        def __init__(self):
            self.current_user_name = "Mike"
            self.current_user_song = "THING"
            self.current_user_artist = "PERSON"
            self.current_user_playing = False
            self.lock = DummyLock()
            print("Starting watcher test")
        
        def add_log_message(self, message):
            print(message)

        def update_current_user_values(self, user):
            print("Updating user to listening to {} - {}".format(user.song, user.artist))

    class DummyLock:
        def __init__(self):
            print("Initting dummy lock")
        def acquire(self):
            print("Acquiring dummy lock")
        def release(self):
            print("Releasing dummy lock")
    
    class DummySender:
        def __init__(self):
            print("Initting dummy sender")
        def update_user(self, user):
            return

    state = DummyState()
    sender = DummySender()
    watcher = SpotifyWatcher(state, sender)
    watcher.start()
