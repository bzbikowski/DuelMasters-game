from PySide6.QtCore import QObject, Signal, Slot 
from PySide6.QtWidgets import QDialog
from src.ui.ui_client import Ui_ClientDialog
from src.ui.ui_server import Ui_ServerDialog


class ClientDialog(QDialog):
    closing = Signal(None)
    paramsReady = Signal(str, str)
    def __init__(self, parent=None):
        super(ClientDialog, self).__init__(parent)
        self.ui = Ui_ClientDialog()
        self.ui.setupUi(self)
        self.ip_addreess = None
        self.port = None
        self.ui.ok_button.clicked.connect(self.verify_data)
        self.ui.back_button.clicked.connect(self.return_to_menu)

        self.ui.ip_address_field.setText("192.168.56.101")
        self.ui.port_field.setText("10023")

    def return_to_menu(self):
        self.closing.emit()
        self.close()

    def verify_data(self):
        ip_addreess = self.ui.ip_address_field.text()
        port = self.ui.port_field.text()

        # TODO: magic

        self.paramsReady.emit(ip_addreess, port)


class ServerDialog(QDialog):
    closing = Signal(None)
    def __init__(self, parent=None):
        super(ServerDialog, self).__init__(parent)
        self.ui = Ui_ServerDialog()
        self.ui.setupUi(self)
        self.ui.back_button.clicked.connect(self.return_to_menu)

    def return_to_menu(self):
        self.closing.emit()
        self.close()