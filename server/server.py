import tornado.web
import tornado.websocket
import tornado.ioloop
import tornado.httpserver
import json
import time
import datetime
import threading

config = json.loads(open('config.json').read())

user_state = []
clients = []
web_ui = open('web_ui.html').read().replace('%HOST_AND_PORT%', "{}:{}".format(config['host'], config['port']))

def get_user(name):
    user = [u for u in user_state if u['name'] == name]
    if len(user) == 0:
        return None
    else:
        return user[0]

def update_user(mdict):
    remove_user = get_user(mdict['user']['name'])
    user_state.remove(remove_user)
    mdict['user']['last_updated'] = datetime.datetime.now().timestamp()
    user_state.append(mdict['user'])
    message = json.dumps({"type":"UPDATE_USER", "user":mdict['user']})
    for client in clients:
        client['socket'].write_message(message)

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        print("New client connected.") 

    def on_message(self, message):
        mdict = json.loads(message)
        
        if mdict['type'] == "UPDATE_USER":
            update_user(mdict)

        elif mdict['type'] == "RECV_CLIENT":
            clients.append({ "name" : mdict['name'], "socket" : self})
        else: 
            self.write_message(write_message(u"{\"type\":\"SUCCESS_RESPONSE\"}"))

    def on_close(self):
        closing_client = [cu for cu in clients if cu['socket'] == self][0]
        closing_user = [u for u in user_state if closing_client['name'] == u['name']][0]
        clients.remove(closing_client)
        user_state.remove(closing_user)
        
        message = json.dumps({"type": "USER_DISCONNECT", "name":closing_user['name']})
        for client in clients:
            client['socket'].write_message(message)

        print("Client disconnected")

class StateHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(json.dumps(user_state))

class UpdateHandler(tornado.web.RequestHandler):
    def post(self):
        data = self.request.body
        print("Received user update: {}".format(data))
        mdict = json.loads(data.decode("UTF-8"))
        update_user(mdict)

class RegisterHandler(tornado.web.RequestHandler):
    def post(self):
        data = self.request.body
        print("Received registration: {}".format(data))
        mdict = json.loads(data.decode("UTF-8"))
        user_state.append(mdict)
        
        update_dict = {'type':"UPDATE_USER", 'user': json.loads(data.decode("UTF-8"))}

        for client in [c for c in clients if c['name'] != mdict['name']]:
            client['socket'].write_message(json.dumps(update_dict))

class WebUIHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(web_ui)

class HeartbeatHandler(tornado.web.RequestHandler):
    def post(self):
        data = self.request.body
        if data == None:
            return
        try:
            dict = json.loads(data.decode("UTF-8"))
            username = dict['user']
            user_entry = get_user(username)
            user_entry['last_updated'] = datetime.datetime.now().timestamp()
        except:
            print("Bad heartbeat received")
            return
 
class Server(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/websocket', WebSocketHandler),
            (r'/state', StateHandler),
            (r'/register', RegisterHandler),
            (r'/update', UpdateHandler),
            (r'/web_ui', WebUIHandler),
            (r'/heartbeat', HeartbeatHandler)
        ]

        tornado.web.Application.__init__(self, handlers)

class InactiveCleaner(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        while(True):
            remove_time = (datetime.datetime.now() - datetime.timedelta(seconds=config['client_timeout'])).timestamp()
            remove_users = [u for u in user_state if 'last_updated' in u and u['last_updated'] < remove_time]

            for timed_out_user in remove_users:
                print("User timed out: {}".format(timed_out_user['name']))
                user_state.remove(timed_out_user)
                
                message = json.dumps({"type": "USER_DISCONNECT", "name":timed_out_user['name']})
                for client in clients:
                    client['socket'].write_message(message)
                
                timed_out_socket_list = [c for c in clients if c['name'] == timed_out_user['name']]
                if len(timed_out_socket_list) == 0:
                    continue
                
                for stale_socket in timed_out_socket_list:
                    clients.remove(stale_socket)
            time.sleep(config['heartbeat_check_interval'])

if __name__ == '__main__':
    ws_app = Server()
    server = tornado.httpserver.HTTPServer(ws_app)
    server.listen(9000)
    cleaner = InactiveCleaner()
    cleaner.start()
    tornado.ioloop.IOLoop.instance().start()
