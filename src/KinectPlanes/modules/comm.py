# -*- coding: utf-8 -*-
"""
Communication Protocols and Factories.
"""
from threading import Thread
import autobahn

########################################################################
########################################################################
########################################################################

LOOP_TIME = 0.1
MESSAGE = "skeleton"

########################################################################
########################################################################
########################################################################

class ClientProtocol(Thread, autobahn.websocket.WebSocketClientProtocol):
    """Protocol for websocket communication"""
    def __init__(self):
        Thread.__init__(self)

    def send_message(self):
        """Sends the message via Websockets"""
        self.sendMessage(MESSAGE)

    def onOpen(self):
        """Action on establishing the connection"""
        self.send_message()

    def onMessage(self, msg, binary):
        """Action on receiving message"""
        self.process_data(msg)
        self.factory.app.reactor.callLater(LOOP_TIME, self.send_message)

    def process_data(self, data):
        """Data processor"""
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