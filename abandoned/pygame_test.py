import pygame
from PyQt5 import QtGui
from PyQt5.QtWidgets import QWidget
import random


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

    def keyPressEvent(self, e):
        pass


class Plane1(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        self.image1 = pygame.image.load("images/plane1_1.png").convert_alpha()
        self.rect = self.image1.get_rect()
        self.mask = pygame.mask.from_surface(self.image1)

        pos1 = random.randint(50, 150)
        pos2 = random.randint(50, 150)
        self.rect.left = pos1
        self.rect.top = pos2
