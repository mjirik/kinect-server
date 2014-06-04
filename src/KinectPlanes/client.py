# -*- coding: utf-8 -*-
"""
Skeleton Viewer.
author: Roman Gerhat
"""
import math
import os
import sys

import qt4reactor
from PySide.QtCore import *
from PySide.QtGui import *
import json

HOST = "ws://127.0.0.1:9002"
#from KinectPlanes.modules.comm import EchoClientProtocol
from KinectPlanes.gui.main_window import MainWindow

########################################################################
########################################################################
########################################################################

class KinectPlanes(QApplication):
    def __init__(self, args):
        QApplication.__init__(self, args)
        self.reactor = None
        self.path = os.path.abspath(os.path.dirname(args[0]))
        self.angle = 0
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
        self.angle = self.get_angle_from_data(json.loads(data))
        
    def get_angle_from_data(self, data):
        skeleton_found = False
        for i, skeleton in enumerate(data):
            if len(skeleton.keys()) is not 0:
                skeleton_found = True
                coords_left = (data[i]["LeftHand"]["X"], data[i]["LeftHand"]["Y"])
                coords_right = (data[i]["RightHand"]["X"], data[i]["RightHand"]["Y"])
        if not skeleton_found:
            tan = 0
        else:
            tan = (float(coords_left[1] - coords_right[1])
                    /float(coords_left[0] - coords_right[0]))
        return math.degrees(math.atan(tan))

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
        
        from KinectPlanes.modules.comm import ClientFactory, ClientProtocol
        
        self.main_window.btn_connect.setEnabled(False)
        self.comm_factory = ClientFactory(self.main_window.edit_add.toPlainText(), self)
        self.comm_factory.protocol = ClientProtocol
        #self.comm_factory.protocol.set_app(self)
        connectWS(self.comm_factory)
        #self.stop()

    def stop(self):
        self.closeAllWindows()
        QApplication.quit()

########################################################################
########################################################################
########################################################################

def main():
    app = QCoreApplication.instance()
    if app == None:
        app = KinectPlanes(sys.argv)
        qt4reactor.install()
        from twisted.internet import reactor
        app.set_reactor(reactor)
    sys.exit(app.start())

if __name__ == '__main__':
    main(sys.argv[0])