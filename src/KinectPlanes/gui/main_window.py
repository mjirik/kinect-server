# -*- coding: utf-8 -*-
"""
Main client window.
"""
import os
import threading

from PySide.QtCore import *
from PySide.QtGui import *

from KinectPlanes.gui.main import Ui_MainWindow
from KinectPlanes.modules.projection import ProjectionCanvas
from KinectPlanes.client import HOST

########################################################################
########################################################################
########################################################################

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, app):
        QMainWindow.__init__(self)
        self.setupUi(self)
        self.app = app
        self.setWindowIcon(QIcon(os.path.abspath(os.path.join(self.app.path, "KinectPlanes", "images", "icon.png"))))
        self.setWindowTitle(u"Kinect Planes")
        self.fill_interface()
        self.connect()

#####################################################
#####################################################

    def connect(self):
        """Links the gui responses"""
        self.btn_start.connect(SIGNAL("clicked()"), self.btn_project_clicked)
        self.btn_connect.connect(SIGNAL("clicked()"), self.app.start_comm)

#####################################################
#####################################################

    def btn_project_clicked(self):
        """Starts/Finishes animations"""
        if self.app.projecting:
            self.stop_projection()
        else:
            self.app.projecting = True
            self.paint_project_button(True)
            threading.Thread(target=self.start_projection).start()

#####################################################
#####################################################

    def start_projection(self):
        """Starts the main animation"""
        self.app.canvas = ProjectionCanvas(self.app)
        self.app.canvas.load()
        self.app.canvas.start()

#####################################################
#####################################################

    def stop_projection(self):
        """Closes the main animation"""
        self.app.projecting = False
        self.paint_project_button(False)
        self.app.canvas.finish()

#####################################################
#####################################################

    def fill_interface(self):
        """Draws the basic gui and its layout"""
        path = os.path.abspath(os.path.join(self.app.path, "KinectPlanes", "images", "bg.png"))
        pixmap = QPixmap(path)
        pixmap = pixmap.scaled(self.width(), self.height())
        palette = QPalette()
        palette.setBrush(QPalette.Background, QBrush(pixmap))
        self.edit_add.setText(HOST)
        self.setPalette(palette)

        self.set_online_status(False)
        self.paint_project_button(False)
        print "filled"
        
#####################################################
#####################################################
    
    def paint_project_button(self, running):
        """Uses the appropriate button image"""
        if running:
            self.btn_start.setIcon(QIcon(
                    os.path.abspath(os.path.join(self.app.path, "KinectPlanes", "images", "red_btn.png"))))
        else:
            self.btn_start.setIcon(QIcon(
                   os.path.abspath(os.path.join(self.app.path, "KinectPlanes", "images", "green_btn.png"))))
        self.btn_start.setIconSize(QSize(
                self.btn_start.width(), self.btn_start.height()))

#####################################################
#####################################################

    def set_online_status(self, status):
        """Notifies when connected to websocket"""
        name = "label"
        label = self.label
        label_sign = self.lbl_online
        text = ["ONLINE", "OFFLINE"]
        if status:
            label.setStyleSheet("#label{color: green;}")
            label.setText(text[0])
            pixmap = QPixmap(os.path.abspath(os.path.join(self.app.path, "KinectPlanes", "images", "green_dot.png")))
        else:
            label.setStyleSheet("#"+name+"{color: red;}")
            label.setText(text[1])
            pixmap = QPixmap(os.path.abspath(os.path.join(self.app.path, "KinectPlanes", "images", "red_dot.png")))
        image = pixmap.scaled(QSize(30, 30))
        label_sign.setPixmap(image)

#####################################################
#####################################################

    def closeEvent(self, event):
        """Closing event to prevent possible problems"""
        self.app.stop()
        event.accept()