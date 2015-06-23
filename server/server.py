from autobahn.asyncio.websocket import WebSocketServerProtocol, \
		WebSocketServerFactory

class MyServerProtocol(WebSocketServerProtocol):
	def onConnect(self, request):
		print("Client connecting: {0}".format(request.peer))
	
	def onOpen(self):
		print("Socket connection open")
	
	def onMessage(self, payload, isBinary):
		if isBinary:
			print("Binary message received: {0} bytes".format(len(payload)))
		else:
			print("Text message received: {0}".format(payload.decode('utf-8')))

		self.sendMessage(payload, isBinary)

	def onClose(self, wasClean, code, reason):
		print("WebSocket connection closed: {0}".format(reason))

if __name__ == '__main__':
	try:
		import asyncio
	except ImportError:
		import trollius as asyncio
	
	factory = WebSocketServerFactory("ws://localhost:9000", debug=False)
	factory.protocol = MyServerProtocol

	loop = asyncio.get_event_loop()
	coro = loop.create_server(factory, '0.0.0.0', 9000)
	server = loop.run_until_complete(coro)

	try:
		loop.run_forever()
	except KeyboardInterrupt:
		pass
	finally:
		server.close()
		loop.close()



