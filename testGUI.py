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
    
    def __init__(self, pics):
        super().__init__()
        uic.loadUi('simpleGUI.ui', self)    
        self.scrollAreaWidgetContents = QLabel()    
        self.scrollArea.setWidget(self.scrollAreaWidgetContents)
        self.spinBox.setMinimum(0)
        self.spinBox.setMaximum(len(pics)-1)  
        self.pics = pics
        self.pixmaps =[QPixmap(a) for a in self.pics] 
        self.spinBox.valueChanged.connect(self.spinChange)
        self.spinBox.setValue(0)
        self.spinChange()
        self.backButton.clicked.connect(self.backClicked)
        self.nextButton.clicked.connect(self.nextClicked)
        
    def backClicked(self):
        if self.spinBox.value == 0:
            return
        else:
            self.spinBox.setValue(self.spinBox.value() -1)
            self.spinChange()
    
    def nextClicked(self):
        if self.spinBox.value == len(self.pics)-1:
            return
        else:
            self.spinBox.setValue(self.spinBox.value() + 1)
            self.spinChange()
            
    def spinChange(self):
        i = self.spinBox.value()
        self.scrollAreaWidgetContents.setPixmap(self.pixmaps[i]) 
                
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    pics = ["rabbit-01.jpg","rabbit-02.jpg","rabbit-03.jpg","rabbit-04.jpg","rabbit-05.jpg","rabbit-06.jpg"]
    ex = Example(pics)
    
    

    ex.show()
    sys.exit(app.exec_())  
