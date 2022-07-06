# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'loading.ui'
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
from PySide6.QtWidgets import (QApplication, QDialog, QLabel, QProgressBar,
    QSizePolicy, QSpacerItem, QVBoxLayout, QWidget)

class Ui_Loading(object):
    def setupUi(self, Loading):
        if not Loading.objectName():
            Loading.setObjectName(u"Loading")
        Loading.resize(400, 300)
        self.verticalLayoutWidget = QWidget(Loading)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(9, 9, 381, 281))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.statusLabel = QLabel(self.verticalLayoutWidget)
        self.statusLabel.setObjectName(u"statusLabel")

        self.verticalLayout.addWidget(self.statusLabel)

        self.statusProgressbar = QProgressBar(self.verticalLayoutWidget)
        self.statusProgressbar.setObjectName(u"statusProgressbar")
        self.statusProgressbar.setValue(0)

        self.verticalLayout.addWidget(self.statusProgressbar)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer)


        self.retranslateUi(Loading)

        QMetaObject.connectSlotsByName(Loading)
    # setupUi

    def retranslateUi(self, Loading):
        Loading.setWindowTitle(QCoreApplication.translate("Loading", u"Dialog", None))
        self.statusLabel.setText(QCoreApplication.translate("Loading", u"TextLabel", None))
    # retranslateUi

