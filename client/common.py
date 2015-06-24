import json
import threading

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

def dummy_log():
    return ["The thing 1", "The thing 2", "The thing 3"]

class User:
    def __init__(self, name, song="", artist="", playing=False):
        self.name = name
        self.song = song
        self.artist = artist
        self.playing = playing
    
    def from_dict(dict):

    def get_song_info(self):
        return "{} - {}".format(self.song, self.artist)

    def toJson(self):
        return json.dumps(self.__dict__)

#This thing is bad and I should feel bad
class ApplicationState:
    def __init__(self, user_name, max_log_length):
        self.current_user_name = user_name
        self.current_user_song = "THE THING"
        self.current_user_artist = "BLARG"
        self.current_user_playing = True
        self.other_users = []
        self.other_users_start_index = 0
        self.log = []
        self.max_log_length = max_log_length
        self.update_current_user = False
        self.update_other_users = False
        self.update_log = False
        self.lock = threading.Lock()

    def reset_update_variables(self):
        self.update_current_user = False
        self.update_other_users = False
        self.update_log = False

    def update_current_song_and_artist(self, song, artist):
        self.current_user_song = song
        self.current_user_artist = artist
        
        self.add_log_entry("You are listening to {}".format(song_string))
        self.update_current_user = True
    
    def add_or_modify_user(self, user):
        matching_users = [u for u in self.other_users if u.name == user.name]
        
        if len(matching_users) < 1:
           log_entry = "User {} connected!".format(user.name) 
           self.add_log_entry(log_entry)
        else:
            if matching_users[0].playing and not user.playing:
                self.add_log_entry("User {} stopped playing music on spotify.".format(user.name))
            elif not matching_users[0].playing and user.playing:
                self.add_log_entry("User {} Started playing music on spotify".format(user.name))

            if matching_users[0].song != user.song or matching_users[0].artist != user.artist:
                self.add_log_entry("User {} now listening to \"{}\"".format(user.name, user.get_song_info()))
        
        self.update_other_users = True
    
    def remove_user(self, name):
        self.other_users = [u for u in self.other_users if u.name != name] 
        self.add_log_entry("User {} disconnected".format(name))
        self.update_other_users = True

    def add_log_entry(self, entry):
        self.log.append(entry)
        log_length = len(self.log)
        if log_length > self.max_log_length:
           self.log = self.log[(self.max_log_length - log_length):]
        self.update_log = True

