from PySide6.QtWidgets import QDialog


from PySide6.QtWidgets import QDialog
from src.ui.ui_connection import Ui_ConnectionMenu

class ConnectionDialog(QDialog):
    def __init__(self, parent=None):
        super(ConnectionDialog, self).__init__(parent)
        self.ui = Ui_ConnectionMenu()
        self.ui.setupUi(self)
        self.ui.server_button.clicked.connect(self.server_mode)
        self.ui.client_button.clicked.connect(self.client_mode)
        self.ui.back_button.clicked.connect(self.return_to_menu)

    def server_mode(self):
        self.done(1)

    def client_mode(self):
        self.done(2)

    def return_to_menu(self):
        self.done(0)