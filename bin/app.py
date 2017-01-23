from autobahn.twisted.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory


class MyServerProtocol(WebSocketServerProtocol):

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def onOpen(self):
        print("WebSocket connection open.")

    def onMessage(self, payload, isBinary):
        if isBinary:
            print("Binary message received: {0} bytes".format(len(payload)))
        else:
            print("Text message received: {0}".format(payload.decode('utf8')))

        # echo back message verbatim
        self.sendMessage(payload, isBinary)

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))


if __name__ == '__main__':

    import sys

    from twisted.python import log
    from twisted.internet import reactor

    log.startLogging(sys.stdout)
	
    factory = WebSocketServerFactory(u"ws://communication-sarahb-s.c9users.io:8081")
    factory.protocol = MyServerProtocol
    factory.setProtocolOptions(maxConnections=2, autoPingInterval=5, autoPingTimeout=2)
	#factory.setProtocolOptions(autoPingInterval=5, autoPingTimeout=2)
    # note to self: if using putChild, the child must be bytes...
    print("here")
    reactor.listenTCP(8081, factory) 
    print("sooooo")
    reactor.run()