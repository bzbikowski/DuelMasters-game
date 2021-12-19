# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'menu.ui'
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
from PySide6.QtWidgets import (QApplication, QGridLayout, QLayout, QPushButton,
    QSizePolicy, QWidget)

class Ui_Menu(object):
    def setupUi(self, Menu):
        if not Menu.objectName():
            Menu.setObjectName(u"Menu")
        Menu.resize(800, 600)
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Menu.sizePolicy().hasHeightForWidth())
        Menu.setSizePolicy(sizePolicy)
        self.gridLayout = QGridLayout(Menu)
        self.gridLayout.setObjectName(u"gridLayout")
        self.main_layout = QGridLayout()
        self.main_layout.setSpacing(18)
        self.main_layout.setObjectName(u"main_layout")
        self.main_layout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.main_layout.setContentsMargins(36, 36, 36, 36)
        self.game_button = QPushButton(Menu)
        self.game_button.setObjectName(u"game_button")
        sizePolicy.setHeightForWidth(self.game_button.sizePolicy().hasHeightForWidth())
        self.game_button.setSizePolicy(sizePolicy)

        self.main_layout.addWidget(self.game_button, 0, 0, 1, 1)

        self.deck_button = QPushButton(Menu)
        self.deck_button.setObjectName(u"deck_button")
        sizePolicy.setHeightForWidth(self.deck_button.sizePolicy().hasHeightForWidth())
        self.deck_button.setSizePolicy(sizePolicy)

        self.main_layout.addWidget(self.deck_button, 0, 1, 1, 1)

        self.manager_button = QPushButton(Menu)
        self.manager_button.setObjectName(u"manager_button")
        sizePolicy.setHeightForWidth(self.manager_button.sizePolicy().hasHeightForWidth())
        self.manager_button.setSizePolicy(sizePolicy)

        self.main_layout.addWidget(self.manager_button, 1, 0, 1, 1)

        self.exit_button = QPushButton(Menu)
        self.exit_button.setObjectName(u"exit_button")
        sizePolicy.setHeightForWidth(self.exit_button.sizePolicy().hasHeightForWidth())
        self.exit_button.setSizePolicy(sizePolicy)

        self.main_layout.addWidget(self.exit_button, 1, 1, 1, 1)


        self.gridLayout.addLayout(self.main_layout, 0, 0, 1, 1)


        self.retranslateUi(Menu)

        QMetaObject.connectSlotsByName(Menu)
    # setupUi

    def retranslateUi(self, Menu):
        Menu.setWindowTitle(QCoreApplication.translate("Menu", u"Main menu", None))
        self.game_button.setText(QCoreApplication.translate("Menu", u"New game", None))
        self.deck_button.setText(QCoreApplication.translate("Menu", u"Load deck", None))
        self.manager_button.setText(QCoreApplication.translate("Menu", u"Deck manager", None))
        self.exit_button.setText(QCoreApplication.translate("Menu", u"Exit an app", None))
    # retranslateUi

