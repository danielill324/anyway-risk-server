from __future__ import division
from autobahn.twisted.websocket import WebSocketServerProtocol, \
    WebSocketServerFactory
from dataFromDb import *
#BH
import sqlite3
import web
import re
import ast
connectDb=DbFunc()
inSquare=-1
idP=-1
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
            if((payload.split())[0]=="lat/lng:"):
                try: 
                    numbers = re.findall(r"(-*\d+\.\d+)", payload)
    	    	    answerFromDb = connectDb.screenColor(numbers[0], numbers[1], numbers[2],numbers[3])
    	    	    self.sendMessage(answerFromDb)
                except:
                    pass
            else:
                try:
                  if((payload.split())[0]=="location"):
                        numbers = re.findall(r"(-*\d+\.\d+)", payload)
                        inSquare=connectDb.find_square(numbers[0], numbers[1])
                        if(inSquare==1):
                            self.sendMessage("2")
                        else:
                            if(inSquare==-1):
                                self.sendMessage("3")
                            
                            
                except:
                    pass
        
    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        self.sendMessage("closed")
        #WebSocketServerProtocol.send_close(code,reason)
        
    
        

if __name__ == '__main__':

    import sys

    from twisted.python import log
    from twisted.internet import reactor
    #conn=DbFunc()
   # conn.screenColor("32.47630332887803", "35.57665307074785", "31.067353465696755", "34.466307014227")
    log.startLogging(sys.stdout)
    factory = WebSocketServerFactory(u"ws://anyway-server-danielill324.c9users.io:8081")
    factory.protocol = MyServerProtocol
    factory.setProtocolOptions(maxConnections=20, autoPingInterval=5, autoPingTimeout=30,echoCloseCodeReason =True)
	#factory.setProtocolOptions(autoPingInterval=5, autoPingTimeout=2)
    # note to self: if using putChild, the child must be bytes...
    reactor.listenTCP(8081, factory) 
    reactor.run()
