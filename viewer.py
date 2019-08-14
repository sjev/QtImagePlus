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
from PyQt5.QtGui import QPixmap, QImage, QTransform

import qimage2ndarray as q2a
import numpy as np
from skimage.color import label2rgb

ZOOM_FACTOR = 1.25

def float2uint8(img):
    return (img*255).astype(np.uint8)

def any2pixmap(img):
    """ convert multiple inputs to pixmap """
    if isinstance(img,np.ndarray): # numpy array
            if img.dtype == np.float:
                image = q2a.array2qimage(float2uint8(img))
            else:
                image = q2a.array2qimage(img)
            pixmap = QPixmap.fromImage(image)
    elif isinstance(img,str): # path to image file
        pixmap = QPixmap(img)
    elif isinstance(img,QImage): # QImage input
        pixmap = QPixmap.fromImage(image)
    else:
        raise ValueError('Incorrect input, must be ndarray, QImage or str')
    return pixmap

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

        self._handles = {'image':None,'labels':None}
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
        """ handle context menu action. the functions are called with (data,self) arguments"""
        
        if self._contextMenu is not None:
            scenePos = self.mapToScene(event.pos())
            act = self._contextMenu.exec_(event.globalPos())
            if act is not None:
                data = {'x':scenePos.x(),'y':scenePos.y()}
                self._contextActions[act](data,self)



    def setImage(self,img):
        """ set image, accepts multiple formats """

        pixmap = any2pixmap(img)

        if self._handles['image'] is not None:
            self.scene.removeItem(self._handles['image'])
            
        self._handles['image'] = self.scene.addPixmap(pixmap)
        
        
    def setLabels(self,labels,opacity=0.5):
        """ the labels are provided as a 2-d numpyarray 
        0 is background
        """
        
        rgb = label2rgb(labels, bg_label=0)
        # generate alpha
        alpha = np.ones(labels.shape)
        alpha[labels==0] = 0
            
        overlay = np.dstack((rgb,alpha))
        pixmap = any2pixmap(overlay)
        
        effect = QGraphicsOpacityEffect()
        effect.setOpacity(opacity)

        item = QGraphicsPixmapItem()
        item.setPixmap(pixmap)
        item.setGraphicsEffect(effect)
        
        
        if self._handles['labels'] is not None:
            self.scene.removeItem(self._handles['labels'])
        
        self.scene.addItem(item)
        self._handles['labels'] = item
        

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
    from testdata import TestData

    print('Using Qt ' + QtCore.QT_VERSION_STR)

    def handleLeftClick(x, y):
        row = int(y)
        column = int(x)
        print("Clicked on image pixel (row="+str(row)+", column="+str(column)+")")

    def testFcn1(data,caller):
        #caller.scene.removeItem(caller._handles['labels'])
        h = caller._handles['image']
        if h.isVisible():
            h.setVisible(False)
        else:
            h.setVisible(True)

    def testFcn2(data,caller):
        print('bar',data)

    # create test data
    tst = TestData()

    # Create the application.
    app = QApplication(sys.argv)
    viewer = QViewer()
    viewer.setImage(tst.image)
    viewer.setLabels(tst.labels)

    # add click handler
    viewer.leftMouseButtonPressed.connect(handleLeftClick)

    # create context menu actions, they will also be called with scene coordinates
    viewer.setContextMenu({'toggle labels':testFcn1,'bar':testFcn2})

    viewer.show()
    app.exec_()