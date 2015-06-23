import threading
import curses

def increment_user_start_index(state, other_users_max_length):
	state.lock.acquire()
	
	users_length = len(state.other_users)
	if (state.other_users_start_index + other_users_max_length) < users_length:
		state.other_users_start_index += 1
		state.update_other_users = True
	
	state.lock.release()


def decrement_user_start_index(state):
	state.lock.acquire()
	if state.other_users_start_index > 0:
		state.other_users_start_index -= 1
		state.update_other_users = True
	state.lock.release()

class KeyWatcher(threading.Thread):
	def __init__(self, stdscr, state, other_users_max_length):
		self.stdscr = stdscr
		self.state = state
		self.other_users_max_length = other_users_max_length
		threading.Thread.__init__(self)
	
	def run(self):
		while True:
			input = self.stdscr.getch()
			if input == curses.KEY_UP:
				increment_user_start_index(self.state, self.other_users_max_length)
			elif input == curses.KEY_DOWN:
				decrement_user_start_index(self.state)

	
