#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 10:54:02 2019

@author: Jev Kuznetsov


The project is inspired by (and contains bits an pieces from): 
     *  https://github.com/marcel-goldschen-ohm/PyQtImageViewer
     * https://github.com/danboid/shufti

"""

from PyQt5 import QtCore
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QGraphicsView, QGraphicsScene, QMenu, QGraphicsOpacityEffect, QGraphicsPixmapItem
from PyQt5.QtGui import QPixmap, QTransform

ZOOM_FACTOR = 1.25

class QViewer(QGraphicsView):

    # Mouse button signals emit image scene (x, y) coordinates.
    # !!! For image (row, column) matrix indexing, row = y and column = x.
    leftMouseButtonPressed = pyqtSignal(float, float)
    rightMouseButtonPressed = pyqtSignal(float, float)
    leftMouseButtonReleased = pyqtSignal(float, float)
    rightMouseButtonReleased = pyqtSignal(float, float)
    leftMouseButtonDoubleClicked = pyqtSignal(float, float)
    rightMouseButtonDoubleClicked = pyqtSignal(float, float)


    def __init__(self):

        QGraphicsView.__init__(self)

        self.aspectRatioMode = Qt.KeepAspectRatio
        # Flags for enabling/disabling mouse interaction.
        self.canZoom = True
        self.canPan = True

         # Image is displayed as a QPixmap in a QGraphicsScene attached to this QGraphicsView.
        self.scene = QGraphicsScene()
        self.setScene(self.scene)

        self.zoom = 1

        self._contextMenu = None
        self._contextActions = {}

    def setContextMenu(self, entries):
        """ add items to context menu 
        the items are provided as a dict {'name':func}
        """
        menu = QMenu()
        for k,v in entries.items():
            act = menu.addAction(k)
            self._contextActions[act] = v  # solution to pass parameters to functions
        self._contextMenu = menu

    def contextMenuEvent(self, event):

        if self._contextMenu is not None:
            scenePos = self.mapToScene(event.pos())
            act = self._contextMenu.exec_(event.globalPos())
            if act is not None:
                self._contextActions[act](scenePos.x(),scenePos.y())


    def loadImage(self,fName):
        """ load image from file """

        pixmap = QPixmap(fName)
        effect = QGraphicsOpacityEffect()

        item = QGraphicsPixmapItem()
        item.setPixmap(pixmap)
        item.setGraphicsEffect(effect)

        self.scene.addItem(item)

    def wheelEvent(self, event):

        #TODO: add recentering to event.x(), event.y())
        moose = event.angleDelta().y()/120
        if moose > 0:
            self.zoomIn()
        elif moose < 0:
            self.zoomOut()

    def mousePressEvent(self, event):
        """ Start mouse pan or zoom mode.
        """
        scenePos = self.mapToScene(event.pos())
        if event.button() == Qt.LeftButton:
            if self.canPan:
                self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.leftMouseButtonPressed.emit(scenePos.x(), scenePos.y())
        QGraphicsView.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        """ Stop mouse pan or zoom mode (apply zoom if valid).
        """
        QGraphicsView.mouseReleaseEvent(self, event)
        scenePos = self.mapToScene(event.pos())
        if event.button() == Qt.LeftButton:
            self.setDragMode(QGraphicsView.NoDrag)
            self.leftMouseButtonReleased.emit(scenePos.x(), scenePos.y())

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



if __name__ == '__main__':

    import sys
    from PyQt5.QtWidgets import QApplication
    print('Using Qt ' + QtCore.QT_VERSION_STR)

    def handleLeftClick(x, y):
        row = int(y)
        column = int(x)
        print("Clicked on image pixel (row="+str(row)+", column="+str(column)+")")

    def foo(x,y):
        print('foo',x,y)

    def bar(x,y):
        print('bar',x,y)

    # Create the application.
    app = QApplication(sys.argv)
    viewer = QViewer()
    viewer.loadImage("img/bender.png")
    viewer.loadImage("img/beer.png")

    # add click handler
    viewer.leftMouseButtonPressed.connect(handleLeftClick)

    # create context menu actions, they will also be called with scene coordinates
    viewer.setContextMenu({'foo':foo,'bar':bar})

    viewer.show()
    app.exec_()