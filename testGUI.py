#!/usr/bin/python3
# -*- coding: utf-8 -*-

"""
ZetCode PyQt5 tutorial 

This example shows an icon
in the titlebar of the window.

author: Jan Bodnar
website: zetcode.com 
last edited: January 2015
"""

import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5 import uic


class Example(QMainWindow):
    
    def __init__(self):
        super().__init__()
        uic.loadUi('simpleGUI.ui', self)        

        
                
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = Example()
    ex.scrollAreaWidgetContents = QLabel()
    pixmap = QPixmap("Rabbit-1.jpg")
    ex.scrollAreaWidgetContents.setPixmap(pixmap) 
    ex.scrollArea.setWidget(ex.scrollAreaWidgetContents)    
    ex.show()
    sys.exit(app.exec_())  
