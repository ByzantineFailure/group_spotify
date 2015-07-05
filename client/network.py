import websocket
import threading
import urllib.request
import json
from common import User

#websocket.enableTrace(True)

def get_server_url(url, port):
    return url + ":" + port

class MessageFactory:
    def get_state():
        message = { 'type': 'GET_STATE' }
        return json.dumps(message)

    def recv_client(user_name):
        message = { 'type' : 'RECV_CLIENT', 'name' : user_name }  
        return json.dumps(message)

    def update_user(user):
        message = { 'type' : 'UPDATE_USER', 'user' : user.toJson() }
        return json.dumps(message)

    def user_disconnect(name):
        message = { 'type' : 'USER_DISCONNECT', 'name' : name }
        return json.dumps(message)

class DataSender:
    def __init__(self, state, config):
        self.state = state
        self.server_url = "http://" + get_server_url(config['server'], config['port'])
        print(self.server_url)

    def update_user(self, user):
        self.__send_post({ "user": user.__dict__ }, self.server_url, 'update') 
    
    def register_self(self, user):
        self.__send_post(user.__dict__, self.server_url, 'register')
    
    def get_state(self):
        url = "{}/state".format(self.server_url)
        print(url)
        content = urllib.request.urlopen(url).read().decode("UTF-8")
        response = json.loads(content) 

        self.state.lock.acquire()
        for user in response:
            updated_user = User(user['name'], user['song'], user['artist'], user['playing'])
            self.state.add_or_modify_user(updated_user)
        self.state.lock.release()

    def __send_post(self, dictionary, server_url, endpoint):
        post_data = json.dumps(dictionary).encode('utf-8')
        req = urllib.request.Request("{}/{}".format(self.server_url, endpoint))
        req.add_header('Content-Type', 'application/json;charset=utf-8')
        req.add_header('Content-Length', len(post_data))
        urllib.request.urlopen(req, post_data)
        
class DataReceiver(threading.Thread):
    def __init__(self, state, config):
        self.state = state
        self.websocket_url = "ws://" + get_server_url(config['server'], config['port']) + "/websocket"
        print(self.websocket_url)
        self.ws = websocket.create_connection(self.websocket_url)
        
        self.ws.send(MessageFactory.recv_client(state.current_user_name))
        self.__stop = False

        threading.Thread.__init__(self)
    
    def stop(self):
        self.__stop = True

    def run(self):
        while True:
            if(self.__stop):
                return
            message = self.ws.recv()
            print("message was: {}".format(message))
            mdict = json.loads(message)
            message_type = mdict['type']
        
            #KNOWN PROBLEM:  This model will miss messages due to lock contention
            if message_type == "UPDATE_USER":
                print("Received UPDATE_USER")
                user_dict = mdict['user']
                updated_user = User(user_dict['name'], user_dict['song'], user_dict['artist'], user_dict['playing'])
                self.state.lock.acquire()
                self.state.add_or_modify_user(updated_user)
                self.state.lock.release()
            
            elif message_type == "USER_DISCONNECT":
                print("Received USER_DISCONNECT")
                self.state.lock.acquire()
                self.state.remove_user(mdict['name'])
                self.state.lock.release()

            else:
                print("Received unrecognized message");
                self.state.lock.acquire()
                self.state.add_log_entry("Received unrecognized message: {}".format(message))
                self.state.lock.release()

if __name__ == '__main__':
    print("Creating connections")
    
    config_file = open("config.json")
    config = json.loads(config_file.read())

    class dummy_state:
        def __init__(self):
            self.user_name = "DUMMY"

    receiver = DataReceiver(dummy_state(), config)
    receiver.start()
    
    sender = DataSender(dummy_state(), config)
    
    while True:
        sender.send_message("Hello, world!")
        input("")
