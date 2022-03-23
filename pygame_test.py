import pygame
from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget


class ImageWidget(QWidget):
    def __init__(self, surface):
        super().__init__()
        w = surface.get_width()
        h = surface.get_height()
        self.data = surface.get_buffer().raw
        self.image = QtGui.QImage(self.data, w, h, QtGui.QImage.Format_RGB32)

    def paintEvent(self, event):
        qp = QtGui.QPainter()
        qp.begin(self)
        qp.drawImage(0, 0, self.image)
        qp.end()



