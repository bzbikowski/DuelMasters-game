from PySide2.QtWidgets import QMainWindow

from src.menu import MainMenu
from src.ui.ui_windows import Ui_Window


class Window(QMainWindow):
    """
    Main window widget, which is just container for MainMenu widget.
    """
    def __init__(self, screen_size=(800, 600), args=None):
        super(Window, self).__init__()
        self.ui = Ui_Window()
        self.ui.setupUi(self)
        if args.debug == "True":
            debug_mode = True
        else:
            debug_mode = False
        width = 800
        height = 600
        # self.setFixedSize(width, height)
        self.move(int((screen_size[0] - width) / 2), int((screen_size[1] - height) / 2) - 20)
        self.setWindowTitle("Duel master - Main menu")
        self.menu = MainMenu(debug_mode, self)
        self.setCentralWidget(self.menu)
        self.show()
