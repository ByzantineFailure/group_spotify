from curses import wrapper
from ui import CurseUI
from key_watcher import KeyWatcher
from network import DataSender, DataReceiver
from common import User, ApplicationState
from spotify_watcher import SpotifyWatcher
import threading
import time
import pprint
import json

config_file = open("config.json")
config = json.loads(config_file.read())

threads = []

user_name = input("Please input your name: ") 
#user_name = "Mike"

def other_users_slice_length(other_users, max_users_height):
    users_length = len(other_users)

    if users_length <= max_users_height:
        return users_length
    else:
        return max_users_height

def main(stdscr):
    user_song = "THE THING"
    ui = CurseUI(stdscr)
    log_max = ui.get_log_height()
    max_users = ui.get_max_users_height()
    #log_max = 25
    #max_users = 4
    state = ApplicationState(user_name, log_max)
        
    ui.draw_ui(user_name, user_song, state.other_users, state.log, True, True, True)
    
    sender = DataSender(state, config)
    sender.get_state()
    sender.register_self(User(user_name, state.current_user_song, state.current_user_artist, state.current_user_playing))

    receiver = DataReceiver(state, config)
    threads.append(receiver)
    receiver.start()
    
    spotify = SpotifyWatcher(state, sender)
    threads.append(spotify)
    spotify.start()

    watcher = KeyWatcher(stdscr, state, max_users)
    threads.append(watcher)
    watcher.start()
    
    while True:
        time.sleep(.1)
        state.lock.acquire()
        
        slice_length = other_users_slice_length(state.other_users, max_users)
        end_index = state.other_users_start_index + slice_length
        users_slice = state.other_users[state.other_users_start_index:end_index]    
        
        ui.draw_ui(state.current_user_name, state.current_user_song, users_slice, state.log,
                state.update_current_user, state.update_other_users, state.update_log)
        
        state.reset_update_variables()

        state.lock.release()
        #print(state.__dict__)
        #input("")

if __name__ == "__main__":
    wrapper(main)
    for thread in threads:
        thread.stop()
    #main(None)
