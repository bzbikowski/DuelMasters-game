# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'manager.ui'
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFormLayout, QGraphicsView,
    QHBoxLayout, QLabel, QLayout, QLineEdit,
    QPushButton, QSizePolicy, QVBoxLayout, QWidget)

from src.views.builder import DeckBuilder

class Ui_Manager(object):
    def setupUi(self, Manager):
        if not Manager.objectName():
            Manager.setObjectName(u"Manager")
        Manager.resize(800, 600)
        self.horizontalLayout = QHBoxLayout(Manager)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.main_layout = QHBoxLayout()
        self.main_layout.setSpacing(5)
        self.main_layout.setObjectName(u"main_layout")
        self.main_layout.setContentsMargins(10, 10, 10, 10)
        self.deck_view = QGraphicsView(Manager)
        self.deck_view.setObjectName(u"deck_view")
        sizePolicy = QSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.MinimumExpanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.deck_view.sizePolicy().hasHeightForWidth())
        self.deck_view.setSizePolicy(sizePolicy)
        self.deck_view.setMinimumSize(QSize(150, 0))

        self.main_layout.addWidget(self.deck_view)

        self.screen_layout = QVBoxLayout()
        self.screen_layout.setObjectName(u"screen_layout")
        self.view = DeckBuilder(Manager)
        self.view.setObjectName(u"view")
        sizePolicy1 = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.view.sizePolicy().hasHeightForWidth())
        self.view.setSizePolicy(sizePolicy1)
        self.view.setMinimumSize(QSize(400, 0))

        self.screen_layout.addWidget(self.view)

        self.button_layout = QHBoxLayout()
        self.button_layout.setObjectName(u"button_layout")
        self.save_button = QPushButton(Manager)
        self.save_button.setObjectName(u"save_button")

        self.button_layout.addWidget(self.save_button)

        self.clear_button = QPushButton(Manager)
        self.clear_button.setObjectName(u"clear_button")

        self.button_layout.addWidget(self.clear_button)

        self.exit_button = QPushButton(Manager)
        self.exit_button.setObjectName(u"exit_button")

        self.button_layout.addWidget(self.exit_button)


        self.screen_layout.addLayout(self.button_layout)


        self.main_layout.addLayout(self.screen_layout)

        self.gui_layout = QVBoxLayout()
        self.gui_layout.setObjectName(u"gui_layout")
        self.gui_layout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.form_layout = QFormLayout()
        self.form_layout.setObjectName(u"form_layout")
        self.form_layout.setSizeConstraint(QLayout.SetDefaultConstraint)
        self.name_label = QLabel(Manager)
        self.name_label.setObjectName(u"name_label")

        self.form_layout.setWidget(0, QFormLayout.LabelRole, self.name_label)

        self.name_input = QLineEdit(Manager)
        self.name_input.setObjectName(u"name_input")
        sizePolicy2 = QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.name_input.sizePolicy().hasHeightForWidth())
        self.name_input.setSizePolicy(sizePolicy2)

        self.form_layout.setWidget(0, QFormLayout.FieldRole, self.name_input)

        self.type_label = QLabel(Manager)
        self.type_label.setObjectName(u"type_label")

        self.form_layout.setWidget(1, QFormLayout.LabelRole, self.type_label)

        self.type_input = QComboBox(Manager)
        self.type_input.setObjectName(u"type_input")
        sizePolicy2.setHeightForWidth(self.type_input.sizePolicy().hasHeightForWidth())
        self.type_input.setSizePolicy(sizePolicy2)

        self.form_layout.setWidget(1, QFormLayout.FieldRole, self.type_input)

        self.civ_label = QLabel(Manager)
        self.civ_label.setObjectName(u"civ_label")

        self.form_layout.setWidget(2, QFormLayout.LabelRole, self.civ_label)

        self.civ_input = QComboBox(Manager)
        self.civ_input.setObjectName(u"civ_input")
        sizePolicy2.setHeightForWidth(self.civ_input.sizePolicy().hasHeightForWidth())
        self.civ_input.setSizePolicy(sizePolicy2)

        self.form_layout.setWidget(2, QFormLayout.FieldRole, self.civ_input)

        self.cost_label = QLabel(Manager)
        self.cost_label.setObjectName(u"cost_label")

        self.form_layout.setWidget(3, QFormLayout.LabelRole, self.cost_label)

        self.cost_input = QLineEdit(Manager)
        self.cost_input.setObjectName(u"cost_input")

        self.form_layout.setWidget(3, QFormLayout.FieldRole, self.cost_input)

        self.power_label = QLabel(Manager)
        self.power_label.setObjectName(u"power_label")

        self.form_layout.setWidget(4, QFormLayout.LabelRole, self.power_label)

        self.power_layout = QHBoxLayout()
        self.power_layout.setObjectName(u"power_layout")
        self.power_option = QComboBox(Manager)
        self.power_option.setObjectName(u"power_option")

        self.power_layout.addWidget(self.power_option)

        self.power_input = QLineEdit(Manager)
        self.power_input.setObjectName(u"power_input")

        self.power_layout.addWidget(self.power_input)


        self.form_layout.setLayout(4, QFormLayout.FieldRole, self.power_layout)


        self.gui_layout.addLayout(self.form_layout)

        self.search_button = QPushButton(Manager)
        self.search_button.setObjectName(u"search_button")
        sizePolicy3 = QSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.search_button.sizePolicy().hasHeightForWidth())
        self.search_button.setSizePolicy(sizePolicy3)

        self.gui_layout.addWidget(self.search_button)


        self.main_layout.addLayout(self.gui_layout)


        self.horizontalLayout.addLayout(self.main_layout)


        self.retranslateUi(Manager)

        QMetaObject.connectSlotsByName(Manager)
    # setupUi

    def retranslateUi(self, Manager):
        Manager.setWindowTitle(QCoreApplication.translate("Manager", u"Manager", None))
        self.save_button.setText(QCoreApplication.translate("Manager", u"Save", None))
        self.clear_button.setText(QCoreApplication.translate("Manager", u"Clear", None))
        self.exit_button.setText(QCoreApplication.translate("Manager", u"Exit", None))
        self.name_label.setText(QCoreApplication.translate("Manager", u"Name", None))
        self.type_label.setText(QCoreApplication.translate("Manager", u"Type", None))
        self.civ_label.setText(QCoreApplication.translate("Manager", u"Civilization", None))
        self.cost_label.setText(QCoreApplication.translate("Manager", u"Cost", None))
        self.power_label.setText(QCoreApplication.translate("Manager", u"Power", None))
        self.search_button.setText(QCoreApplication.translate("Manager", u"Search", None))
    # retranslateUi

