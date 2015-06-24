import tornado.web
import tornado.websocket
import tornado.ioloop
import tornado.httpserver
import json

user_state = []
clients = []

def update_user(mdict):
    remove_user = [u for u in user_state if u['name'] == mdict['user']['name']][0]
    user_state.remove(remove_user)
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

class Server(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r'/websocket', WebSocketHandler),
            (r'/state', StateHandler),
            (r'/register', RegisterHandler),
            (r'/update', UpdateHandler)
        ]

        tornado.web.Application.__init__(self, handlers)

if __name__ == '__main__':
    ws_app = Server()
    server = tornado.httpserver.HTTPServer(ws_app)
    server.listen(9000)
    tornado.ioloop.IOLoop.instance().start()
