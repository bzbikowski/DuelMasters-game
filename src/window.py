from PySide2.QtWidgets import QMainWindow

from src.menu import MainMenu


class Window(QMainWindow):
    """
    Main window widget, which is just container for MainMenu widget.
    """
    def __init__(self, screen_size=(800, 600), args=None):
        super(Window, self).__init__()
        if args.debug == "True":
            debug_mode = True
        else:
            debug_mode = False
        width = 800
        height = 600
        self.setFixedSize(width, height)
        self.move((screen_size[0] - width)/2, (screen_size[1] - height)/2 - 20)
        self.setWindowTitle("Duel master - Main menu")
        self.ui = MainMenu(debug_mode, self)
        self.setCentralWidget(self.ui)
        self.show()
