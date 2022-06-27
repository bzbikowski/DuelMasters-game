# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'connection.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QPushButton, QSizePolicy,
    QVBoxLayout, QWidget)

class Ui_ConnectionDialog(object):
    def setupUi(self, ConnectionDialog):
        if not ConnectionDialog.objectName():
            ConnectionDialog.setObjectName(u"ConnectionDialog")
        ConnectionDialog.resize(400, 300)
        self.verticalLayoutWidget = QWidget(ConnectionDialog)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(9, 9, 381, 281))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setSpacing(18)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.server_button = QPushButton(self.verticalLayoutWidget)
        self.server_button.setObjectName(u"server_button")
        sizePolicy = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.server_button.sizePolicy().hasHeightForWidth())
        self.server_button.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.server_button)

        self.client_button = QPushButton(self.verticalLayoutWidget)
        self.client_button.setObjectName(u"client_button")
        sizePolicy.setHeightForWidth(self.client_button.sizePolicy().hasHeightForWidth())
        self.client_button.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.client_button)

        self.back_button = QPushButton(self.verticalLayoutWidget)
        self.back_button.setObjectName(u"back_button")
        sizePolicy.setHeightForWidth(self.back_button.sizePolicy().hasHeightForWidth())
        self.back_button.setSizePolicy(sizePolicy)

        self.verticalLayout.addWidget(self.back_button)


        self.retranslateUi(ConnectionDialog)

        QMetaObject.connectSlotsByName(ConnectionDialog)
    # setupUi

    def retranslateUi(self, ConnectionDialog):
        ConnectionDialog.setWindowTitle(QCoreApplication.translate("ConnectionDialog", u"Choose connection", None))
        self.server_button.setText(QCoreApplication.translate("ConnectionDialog", u"Create a game room", None))
        self.client_button.setText(QCoreApplication.translate("ConnectionDialog", u"Connect to existing game", None))
        self.back_button.setText(QCoreApplication.translate("ConnectionDialog", u"Back to menu", None))
    # retranslateUi

