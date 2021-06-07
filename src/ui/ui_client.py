# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'client.ui'
##
## Created by: Qt User Interface Compiler version 5.15.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class Ui_ClientDialog(object):
    def setupUi(self, ClientDialog):
        if not ClientDialog.objectName():
            ClientDialog.setObjectName(u"ClientDialog")
        ClientDialog.resize(400, 300)
        self.verticalLayoutWidget = QWidget(ClientDialog)
        self.verticalLayoutWidget.setObjectName(u"verticalLayoutWidget")
        self.verticalLayoutWidget.setGeometry(QRect(10, 10, 381, 281))
        self.verticalLayout = QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout = QFormLayout()
        self.formLayout.setObjectName(u"formLayout")
        self.formLayout.setFieldGrowthPolicy(QFormLayout.AllNonFixedFieldsGrow)
        self.ip_address_label = QLabel(self.verticalLayoutWidget)
        self.ip_address_label.setObjectName(u"ip_address_label")

        self.formLayout.setWidget(0, QFormLayout.LabelRole, self.ip_address_label)

        self.ip_address_field = QLineEdit(self.verticalLayoutWidget)
        self.ip_address_field.setObjectName(u"ip_address_field")

        self.formLayout.setWidget(0, QFormLayout.FieldRole, self.ip_address_field)

        self.port_label = QLabel(self.verticalLayoutWidget)
        self.port_label.setObjectName(u"port_label")

        self.formLayout.setWidget(1, QFormLayout.LabelRole, self.port_label)

        self.port_field = QLineEdit(self.verticalLayoutWidget)
        self.port_field.setObjectName(u"port_field")

        self.formLayout.setWidget(1, QFormLayout.FieldRole, self.port_field)


        self.verticalLayout.addLayout(self.formLayout)

        self.horizontalLayout = QHBoxLayout()
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(-1, 0, -1, -1)
        self.ok_button = QPushButton(self.verticalLayoutWidget)
        self.ok_button.setObjectName(u"ok_button")

        self.horizontalLayout.addWidget(self.ok_button)

        self.back_button = QPushButton(self.verticalLayoutWidget)
        self.back_button.setObjectName(u"back_button")

        self.horizontalLayout.addWidget(self.back_button)


        self.verticalLayout.addLayout(self.horizontalLayout)


        self.retranslateUi(ClientDialog)

        QMetaObject.connectSlotsByName(ClientDialog)
    # setupUi

    def retranslateUi(self, ClientDialog):
        ClientDialog.setWindowTitle(QCoreApplication.translate("ClientDialog", u"Connect", None))
        self.ip_address_label.setText(QCoreApplication.translate("ClientDialog", u"Ip address", None))
        self.port_label.setText(QCoreApplication.translate("ClientDialog", u"Port", None))
        self.ok_button.setText(QCoreApplication.translate("ClientDialog", u"Accept", None))
        self.back_button.setText(QCoreApplication.translate("ClientDialog", u"Return to menu", None))
    # retranslateUi

