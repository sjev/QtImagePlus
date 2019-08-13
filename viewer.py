#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 13 10:54:02 2019

@author: Jev Kuznetsov
"""

from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt














if __name__ == '__main__':

    import sys
    from PyQt5.QtWidgets import QApplication
    print('Using Qt ' + QtCore.QT_VERSION_STR)


    class MainWindow(QtWidgets.QMainWindow):
        def __init__(self):
            super().__init__()
    
            self.label = QtWidgets.QLabel()
            canvas = QtGui.QPixmap("img/bender.png")
            self.label.setPixmap(canvas)
            self.setCentralWidget(self.label)


    # Create the application.
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    app.exec_()