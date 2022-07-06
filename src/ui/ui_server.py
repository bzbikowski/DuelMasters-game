# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'server.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QLabel, QPushButton,
    QSizePolicy, QVBoxLayout, QWidget)

class Ui_ServerDialog(object):
    def setupUi(self, ServerDialog):
        if not ServerDialog.objectName():
            ServerDialog.setObjectName(u"ServerDialog")
        ServerDialog.resize(400, 300)
        self.verticalLayoutWidget = QWidget(ServerDialog)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(10, 10, 381, 281))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.port_label = QLabel(self.verticalLayoutWidget)
        self.port_label.setObjectName(u"port_label")

        self.verticalLayout.addWidget(self.port_label)

        self.status_label = QLabel(self.verticalLayoutWidget)
        self.status_label.setObjectName(u"status_label")
        self.status_label.setAlignment(Qt.AlignLeading|Qt.AlignLeft|Qt.AlignVCenter)

        self.verticalLayout.addWidget(self.status_label)

        self.back_button = QPushButton(self.verticalLayoutWidget)
        self.back_button.setObjectName(u"back_button")

        self.verticalLayout.addWidget(self.back_button)


        self.retranslateUi(ServerDialog)

        QMetaObject.connectSlotsByName(ServerDialog)
    # setupUi

    def retranslateUi(self, ServerDialog):
        ServerDialog.setWindowTitle(QCoreApplication.translate("ServerDialog", u"Waiting for connection", None))
        self.port_label.setText(QCoreApplication.translate("ServerDialog", u"TextLabel", None))
        self.status_label.setText(QCoreApplication.translate("ServerDialog", u"TextLabel", None))
        self.back_button.setText(QCoreApplication.translate("ServerDialog", u"Return to menu", None))
    # retranslateUi

