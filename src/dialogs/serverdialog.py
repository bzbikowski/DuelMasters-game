from PySide6.QtCore import QObject, Signal, Slot 
from PySide6.QtWidgets import QDialog
from src.ui.ui_server import Ui_ServerDialog


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