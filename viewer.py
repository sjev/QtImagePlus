#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 10:54:02 2019

@author: Jev Kuznetsov


The project is inspired by (and contains bits an pieces from): 
     *  https://github.com/marcel-goldschen-ohm/PyQtImageViewer
     * https://github.com/danboid/shufti

"""

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QMainWindow
from PyQt5.QtGui import QPixmap, QTransform

ZOOM_FACTOR = 1.25

class QViewer(QGraphicsView):

    def __init__(self):

        QGraphicsView.__init__(self)

         # Image is displayed as a QPixmap in a QGraphicsScene attached to this QGraphicsView.
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        self.zoom = 1


    def loadImage(self,fName):
        """ load image from file """

        pixmap = QPixmap(fName)
        self.scene.addPixmap(pixmap)

    def wheelEvent(self, event):

        moose = event.angleDelta().y()/120
        if moose > 0:
            self.zoomIn()
        elif moose < 0:
            self.zoomOut()


    def zoomIn(self):
        self.zoom *= ZOOM_FACTOR
        self.updateView()

    def zoomOut(self):
        self.zoom /= ZOOM_FACTOR
        self.updateView()

    def zoomReset(self):

        self.zoom = 1
        self.updateView()

    def updateView(self):
        self.setTransform(QTransform().scale(self.zoom, self.zoom))

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
    
        self.viewer = QViewer()
        self.viewer.loadImage("img/bender.png")
        self.setCentralWidget(self.viewer)



if __name__ == '__main__':

    import sys
    from PyQt5.QtWidgets import QApplication
    print('Using Qt ' + QtCore.QT_VERSION_STR)




    # Create the application.
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()