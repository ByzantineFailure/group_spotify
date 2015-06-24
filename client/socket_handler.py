import websocket
import threading
import urllib.request
import json
from common import User

#websocket.enableTrace(True)

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
    def __init__(self, state):
        self.state = state
    
    def update_user(self, user):
        self.__send_post({ "user": user.__dict__ }, 'update') 
    
    def register_self(self, user):
        self.__send_post(user.__dict__, 'register')
    
    def get_state(self):
        content = urllib.request.urlopen("http://localhost:9000/state").read().decode("UTF-8")
        response = json.loads(content) 

        self.state.lock.acquire()
        for user in response:
            updated_user = User(user['name'], user['song'], user['artist'], user['playing'])
            self.state.add_or_modify_user(updated_user)
        self.state.lock.release()

    def __send_post(self, dictionary, endpoint):
        post_data = json.dumps(dictionary).encode('utf-8')
        req = urllib.request.Request("http://localhost:9000/{}".format(endpoint))
        req.add_header('Content-Type', 'application/json;charset=utf-8')
        req.add_header('Content-Length', len(post_data))
        urllib.request.urlopen(req, post_data)
        
class DataReceiver(threading.Thread):
    def __init__(self, state):
        self.state = state
        self.ws = websocket.create_connection("ws://localhost:9000/websocket")
        
        self.ws.send(MessageFactory.recv_client(state.current_user_name))

        threading.Thread.__init__(self)

    def run(self):
        while True:
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
    
    class dummy_state:
        def __init__(self):
            self.user_name = "DUMMY"

    receiver = DataReceiver(dummy_state())
    receiver.start()
    
    sender = DataSender()
    
    while True:
        sender.send_message("Hello, world!")
        input("")
