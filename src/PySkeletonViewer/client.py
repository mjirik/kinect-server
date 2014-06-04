# -*- coding: utf-8 -*-
"""
Skeleton Viewer.
author: Roman Gerhat
"""
import os
import sys
import threading

import qt4reactor
from PySide.QtCore import *
from PySide.QtGui import *
import json

HOST = "ws://127.0.0.1:9002"
#from PySkeletonViewer.modules.comm import EchoClientProtocol
from PySkeletonViewer.gui.main_window import MainWindow

########################################################################
########################################################################
########################################################################

VIEW_WIDTH = 2400.
VIEW_HEIGHT = 1800.
WIDTH = 1024.
HEIGHT = 768.
WIDTH_RATIO = WIDTH/VIEW_WIDTH
HEIGHT_RATIO = HEIGHT/VIEW_HEIGHT

########################################################################
########################################################################
########################################################################

class SkeletonViewer(QApplication):
    def __init__(self, args):
        QApplication.__init__(self, args)
        self.reactor = None
        self.path = os.path.abspath(os.path.dirname(args[0]))
        self.skeletons = []
        self.projecting = False
        
        self.comm_factory = None
        self.main_window = None
        self.canvas = None

#####################################################
#####################################################

    def set_reactor(self, reactor):
        self.reactor = reactor

#####################################################
#####################################################

    def save_data(self, data):
        skeletons = []
        for skeleton in json.loads(data):
            joints = {}
            if len(skeleton.keys()) is not 0:
                for joint in skeleton.keys():
                    coords = {
                        "X": int(round((skeleton[joint]["X"] + VIEW_WIDTH/2.)*WIDTH_RATIO)),
                        "Y": int(round((-skeleton[joint]["Y"] + VIEW_HEIGHT/2.)*HEIGHT_RATIO)),
                        "Z": int(round(skeleton[joint]["Z"]))
                             }
                    joints[joint] = coords
                skeletons.append(joints)
        self.skeletons = skeletons

#####################################################
#####################################################

    def start(self):
        self.main_window = MainWindow(self)
        self.main_window.show()
        self.start_comm()
        self.reactor.run()
        self.stop
        print "started"

    def start_comm(self):
        """Starts the communication using websockets"""
        from autobahn.websocket import connectWS, WebSocketClientFactory, WebSocketClientProtocol
        
        from PySkeletonViewer.modules.comm import ClientFactory, ClientProtocol
        
        self.main_window.btn_connect.setEnabled(False)
        self.comm_factory = ClientFactory(self.main_window.edit_add.toPlainText(),self)
        self.comm_factory.protocol = ClientProtocol
        #self.comm_factory.protocol.set_app(self)
        print "connecting"
        connectWS(self.comm_factory)
        #self.stop()

    def stop(self):
        self.closeAllWindows()
        QApplication.quit()

########################################################################
########################################################################
########################################################################

#APP = None

def main():
    app = QCoreApplication.instance()
    if app == None:
        app = SkeletonViewer(sys.argv)
        qt4reactor.install()
        from twisted.internet import reactor
        app.set_reactor(reactor)
    sys.exit(app.start())

if __name__ == '__main__':
    main(sys.argv[0])
