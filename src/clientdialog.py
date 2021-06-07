from PySide2.QtCore import QObject, Signal, Slot 
from PySide2.QtWidgets import QDialog
from src.ui.ui_client import Ui_ClientDialog

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

    def return_to_menu(self):
        self.closing.emit()
        self.close()

    def verify_data(self):
        ip_addreess = self.ui.ip_address_field.text()
        port = self.ui.port_field.text()

        # TODO: magic

        self.paramsReady.emit(ip_addreess, port)