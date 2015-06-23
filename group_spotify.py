#!/usr/bin/python3 
from curses import wrapper
from ui import CurseUI

user_name = "Mike" #input("Please input your name: ")

class User:
	def __init__(self, name, song):
		self.name = name
		self.song = song

def dummy_log():
	return ["The thing 1", "The thing 2", "The thing 3"]

def dummy_users():
	user1 = User("Bob", "Song")
	user2 = User("Frank", "That other song")
	user3 = User("Laura", "Booo")
	user4 = User("Carl", "gibberishsong")

	return [user1, user2, user3, user4]

def main(stdscr):
	user_song = "THE THING"
	ui = CurseUI(stdscr)

	log_max = ui.get_log_height()
	max_users = ui.get_max_users_height()
		
	ui.draw_ui(user_name, user_song, dummy_users(), 0, dummy_log(), True, True, True)
	stdscr.getch()

wrapper(main)
