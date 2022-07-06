from PySide6.QtCore import QObject, Signal, Slot 
from PySide6.QtWidgets import QDialog
from src.ui.ui_loading import Ui_Loading


class LoadingDialog(QDialog):
    closing = Signal(None)
    paramsReady = Signal(str, str)
    def __init__(self, parent=None):
        super(LoadingDialog, self).__init__(parent)
        self.ui = Ui_Loading()
        self.ui.setupUi(self)
        
        self.ui.statusLabel.setText("Loading resources")
        self.ui.statusProgressbar.setValue(0)

    def set_status(self, text, percent):
        self.ui.statusLabel.setText(text)
        self.ui.statusProgressbar.setValue(percent)
