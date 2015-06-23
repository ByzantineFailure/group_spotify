import curses

max_users_height = 4
other_users_border_width = 2

class CurseUI:
	def __init__(self, stdscr):
		screen_height = curses.LINES - 1
		screen_width = curses.COLS - 1
		stdscr.border(1)
		self.screen = stdscr

		window_width = screen_width - 2
		
		current_user_height = 1
		current_user_start_y = 0
		current_user_start_x = 1

		other_users_height = max_users_height + 2 * other_users_border_width
		other_users_start_y = current_user_start_y + current_user_height
		other_users_start_x = 1

		self.log_height = screen_height - current_user_height - other_users_height + 1
		log_start_x = 1
		log_start_y = other_users_start_y + other_users_height

		self.current_user_window = stdscr.subwin(current_user_height, window_width, current_user_start_y, current_user_start_x)
		self.other_users_window = stdscr.subwin(other_users_height, window_width, other_users_start_y, other_users_start_x)
		self.log_window = stdscr.subwin(log_start_y, log_start_x)
	
	def get_log_height(self):
		return self.log_height

	def get_max_users_height(self):
		return max_users_height

	def draw_ui(self, current_user_name, current_user_song, other_users, other_users_start_index, 
			log, update_current_user, update_other_users, update_log):
		if update_current_user:
			self.__draw_current_user_info(current_user_name, current_user_song)
		if update_other_users:
			self.__draw_other_user_list(other_users, other_users_start_index)
		if update_log:
			self.__draw_log_window(log)

	def __draw_current_user_info(self, user_name, user_song):
		self.current_user_window.clear()
		self.current_user_window.addstr(0, 1, "YOUR NAME: {}     YOUR SONG: {}".format(user_name, user_song))
		self.current_user_window.refresh()

#Assumes users_start_index + max_users_height <= users.length - 1
	def __draw_other_user_list(self, users, users_start_index):
		self.other_users_window.clear()
		self.other_users_window.border(other_users_border_width)
		self.other_users_window.addstr(1, 1, "ACTIVE USERS:")

		if len(users) > 0:
			current_user_index = 0
			while current_user_index + users_start_index < len(users) - 1 and current_user_index < max_users_height:
				current_user = users[current_user_index + users_start_index];
				self.other_users_window.addstr(2 + current_user_index, 1, "{} - {}".format(current_user.name, current_user.song));
				current_user_index += 1
				
		else:
			self.other_users_window.addstr(1, 0, "NO OTHER USERS YET")
		self.other_users_window.refresh()

	def __draw_log_window(self, log_info):
		self.log_window.clear()
		for idx, val in enumerate(log_info):
			self.log_window.addstr(idx, 0, "{}".format(val))
		self.log_window.refresh()

