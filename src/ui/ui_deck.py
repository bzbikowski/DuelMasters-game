# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'deck.ui'
##
## Created by: Qt User Interface Compiler version 5.15.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *


class Ui_Deck(object):
    def setupUi(self, Deck):
        if not Deck.objectName():
            Deck.setObjectName(u"Deck")
        Deck.resize(800, 600)
        self.verticalLayoutWidget = QWidget(Deck)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(10, 10, 771, 571))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.graphicsView = QGraphicsView(self.verticalLayoutWidget)
        self.graphicsView.setObjectName(u"graphicsView")

        self.verticalLayout.addWidget(self.graphicsView)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.closeButton = QPushButton(self.verticalLayoutWidget)
        self.closeButton.setObjectName(u"closeButton")

        self.horizontalLayout.addWidget(self.closeButton)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(Deck)

        QMetaObject.connectSlotsByName(Deck)
    # setupUi

    def retranslateUi(self, Deck):
        Deck.setWindowTitle(QCoreApplication.translate("Deck", u"Deck", None))
        self.closeButton.setText(QCoreApplication.translate("Deck", u"Close", None))
    # retranslateUi

