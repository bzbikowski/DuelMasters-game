# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'common.ui'
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

class Ui_CommonDialog(object):
    def setupUi(self, CommonDialog):
        if not CommonDialog.objectName():
            CommonDialog.setObjectName(u"CommonDialog")
        CommonDialog.resize(800, 600)
        self.verticalLayoutWidget = QWidget(CommonDialog)
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
        self.selectButton = QPushButton(self.verticalLayoutWidget)
        self.selectButton.setObjectName(u"selectButton")

        self.horizontalLayout.addWidget(self.selectButton)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(CommonDialog)

        QMetaObject.connectSlotsByName(CommonDialog)
    # setupUi

    def retranslateUi(self, CommonDialog):
        CommonDialog.setWindowTitle(QCoreApplication.translate("CommonDialog", u"Select cards", None))
        self.selectButton.setText(QCoreApplication.translate("CommonDialog", u"Ok", None))
    # retranslateUi

