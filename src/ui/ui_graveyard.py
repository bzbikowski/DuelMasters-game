# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'graveyard.ui'
##
## Created by: Qt User Interface Compiler version 6.2.2
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGraphicsView, QHBoxLayout, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_Graveyard(object):
    def setupUi(self, Graveyard):
        if not Graveyard.objectName():
            Graveyard.setObjectName(u"Graveyard")
        Graveyard.resize(800, 600)
        self.verticalLayoutWidget = QWidget(Graveyard)
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


        self.retranslateUi(Graveyard)

        QMetaObject.connectSlotsByName(Graveyard)
    # setupUi

    def retranslateUi(self, Graveyard):
        Graveyard.setWindowTitle(QCoreApplication.translate("Graveyard", u"Graveyard", None))
        self.closeButton.setText(QCoreApplication.translate("Graveyard", u"Close", None))
    # retranslateUi

