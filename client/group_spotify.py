#!/usr/bin/python3 
from curses import wrapper
from ui import CurseUI
from key_watcher import KeyWatcher
import threading
import time

user_name = "Mike" #input("Please input your name: ")

class User:
    def __init__(self, name, song):
        self.name = name
        self.song = song

class ApplicationState:
    def __init__(self, user_name):
        self.current_user_name = user_name
        self.current_user_song = "THE THING"
        self.current_user_playing = True
        self.other_users = dummy_users()
        self.other_users_start_index = 0
        self.log = dummy_log()
        self.update_current_user = False
        self.update_other_users = False
        self.update_log = False
        self.lock = threading.Lock()

    def reset_update_variables(self):
        self.update_current_user = False
        self.update_other_users = False
        self.update_log = False

def dummy_log():
    return ["The thing 1", "The thing 2", "The thing 3"]

def dummy_users():
    user1 = User("Bob", "Song")
    user2 = User("Frank", "That other song")
    user3 = User("Laura", "Booo")
    user4 = User("Carl", "gibberishsong")
    user5 = User("Bobert", "asdfe")
    user6 = User("Carly", "This is a so song")
    user7 = User("Leonard Nimoy", "Summersong")
    user8 = User("Robb Stark", "The Rains of Castimere")

    return [user1, user2, user3, user4, user5, user6, user7, user8]

def other_users_slice_length(other_users, max_users_height):
    users_length = len(other_users)

    if users_length <= max_users_height:
        return users_length
    else:
        return max_users_height

def main(stdscr):
    user_song = "THE THING"
    ui = CurseUI(stdscr)
    state = ApplicationState(user_name)

    log_max = ui.get_log_height()
    max_users = ui.get_max_users_height()
        
    ui.draw_ui(user_name, user_song, dummy_users()[0:4], dummy_log(), True, True, True)
    watcher = KeyWatcher(stdscr, state, max_users)
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
        
wrapper(main)
