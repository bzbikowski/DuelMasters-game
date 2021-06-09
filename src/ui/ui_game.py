# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'game.ui'
##
## Created by: Qt User Interface Compiler version 5.15.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_Game(object):
    def setupUi(self, Game):
        if not Game.objectName():
            Game.setObjectName(u"Game")
        Game.resize(1360, 768)
        self.view = QGraphicsView(Game)
        self.view.setObjectName(u"view")
        self.view.setGeometry(QRect(0, 0, 1024, 768))
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setSceneRect(QRectF(0, 0, 1024, 768))
        self.preview = QGraphicsView(Game)
        self.preview.setObjectName(u"preview")
        self.preview.setGeometry(QRect(1024, 0, 336, 768))
        self.preview.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.preview.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.preview.setSceneRect(QRectF(0, 0, 336, 768))

        self.retranslateUi(Game)

        QMetaObject.connectSlotsByName(Game)
    # setupUi

    def retranslateUi(self, Game):
        Game.setWindowTitle(QCoreApplication.translate("Game", u"Duel masters - Video game", None))
    # retranslateUi

