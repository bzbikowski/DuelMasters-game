from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import Qt

from src.menu import MainMenu
from src.ui.ui_window import Ui_Window


class Window(QMainWindow):
    """
    Main window widget, which is just container for MainMenu widget.
    """
    def __init__(self, args=None):
        super(Window, self).__init__()
        self.ui = Ui_Window()
        self.ui.setupUi(self)
        if args.debug == "True":
            debug_mode = True
        else:
            debug_mode = False
        self.setWindowState(Qt.WindowMaximized)
        self.setWindowTitle("Duel master - Main menu")
        self.menu = MainMenu(debug_mode, self)
        self.setCentralWidget(self.menu)
        