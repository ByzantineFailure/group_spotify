import threading
import sys
import subprocess
import time
from common import User
import ctypes

class SpotifyWatcher(threading.Thread):
    def __init__(self, state, data_sender):
        current_os = sys.platform
        self.state = state
        self.data_sender = data_sender
        self.valid_os = True
        self.__stop = False
        
        if "darwin" in current_os:
            self.scraper = AppleSpotifyScraper(self.state.current_user_name, self.state.current_user_song, self.state.current_user_artist)
        elif "win32" in current_os:
            self.scraper = WindowsSpotifyScraper(self.state.current_user_name, self.state.current_user_song, self.state.current_user_artist)
        else:
            self.valid_os = False
            self.state.add_log_message("Not running on a supported OS!  Cannot detect spotify song.")
            self.scraper = DummyScraper(self.state.current_user_name)
        
        threading.Thread.__init__(self)

    def stop(self):
        self.__stop = True

    def run(self):
        if not self.valid_os:
            return

        while True:
            if self.__stop:
                return
            user_update = self.scraper.scrape()
            
            if user_update.song != self.state.current_user_song or user_update.artist != self.state.current_user_artist or user_update.playing != self.state.current_user_playing:
                self.data_sender.update_user(user_update)      

            self.state.lock.acquire()
            self.state.update_current_user_values(user_update)
            self.state.lock.release()
            
            time.sleep(1)

class AppleSpotifyScraper:
    def __init__(self, user_name, user_song, user_artist):
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

class WindowsSpotifyScraper:
    def __init__(self, user_name, user_song, user_artist):
        print("Windows Spotify scraper created")
        self.user_name = user_name
        self.user_song = user_song
        self.user_artist = user_artist
        self.spotify_pids = []
        self.__get_spotify_pids()

    def __get_spotify_pids(self):
        tasklist = subprocess.Popen("tasklist.exe /FI \"IMAGENAME eq spotify.exe\"", shell=True, stdout=subprocess.PIPE).communicate()[0].decode("UTF-8")
        tasks = tasklist.split("\r\n")[3:]
        for entry in tasks:
            split = entry.split()
            if len(split) > 1:
                self.spotify_pids.append(int(split[1]))

    def scrape(self):
        EnumWindows = ctypes.windll.user32.EnumWindows
        EnumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.POINTER(ctypes.c_int), ctypes.POINTER(ctypes.c_int))
        GetWindowText = ctypes.windll.user32.GetWindowTextW
        GetWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
        IsWindowVisible = ctypes.windll.user32.IsWindowVisible
        GetWindowThreadProcessId = ctypes.windll.user32.GetWindowThreadProcessId
        titles = []
        
        def foreach_window(hwnd, lParam):
            if not IsWindowVisible(hwnd):
                return True
            pidbuff = ctypes.POINTER(ctypes.c_ulong)(ctypes.c_ulong(1))
            GetWindowThreadProcessId(hwnd, pidbuff)
            pid = pidbuff.contents.value
            length = GetWindowTextLength(hwnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            GetWindowText(hwnd, buff, length + 1)
            if buff.value == "":
                return True
            if not pid in self.spotify_pids:
                return True 

            titles.append(buff.value)

            return True
        EnumWindows(EnumWindowsProc(foreach_window), 0)
        
        result = titles[0]
        if result == "Spotify":
            return User(self.user_name, self.user_song, self.user_artist, False)
        else:
            spl = result.split("-")
            print(spl)
            return User(self.user_name, spl[0].strip(), "-".join(spl[1:]).strip(), True)

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
            print("Updating user to listening to {} - {} - (playing: {})".format(user.song, user.artist, user.playing))

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
    try:
        while True:
            time.sleep(1)
            continue
    finally:
        watcher.stop()
