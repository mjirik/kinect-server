# -*- coding: utf-8 -*-
"""
Communication Protocols and Factories.
"""
from threading import Thread
import autobahn
import twisted

########################################################################
########################################################################
########################################################################

LOOP_TIME = 0.05

########################################################################
########################################################################
########################################################################

class ClientProtocol(autobahn.websocket.WebSocketClientProtocol):
    """Protocol for websocket communication"""
#    def __init__(self):
#        Thread.__init__(self)

    def send_message(self):
        self.sendMessage("skeleton")
 
    def onOpen(self):
        self.send_message()
 
    def onMessage(self, msg, binary):
        self.process_data(msg)
        self.factory.app.reactor.callLater(LOOP_TIME, self.send_message)
        
    def process_data(self, data):
        self.factory.app.save_data(data)
        
########################################################################
########################################################################
########################################################################

class ClientFactory(autobahn.websocket.WebSocketClientFactory):
    
    #self.protocol = WebSocketClientProtocol
    
    def __init__(self, host, app):
        autobahn.websocket.WebSocketClientFactory.__init__(self, url=host, debug=False)
        self.app = app

#####################################################
#####################################################
        
    def clientConnectionLost(self, connector, reason):
        self.app.main_window.set_online_status(False)
        self.app.main_window.btn_connect.setEnabled(True)
        print "connection lost"
    
    def clientConnectionFailed(self, connector, reason):
        self.app.main_window.set_online_status(False)
        self.app.main_window.btn_connect.setEnabled(True)
        print "connection failed"