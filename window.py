from PyQt5.QtWidgets import QMainWindow
from menu import MainMenu


class Window(QMainWindow):
    """
    Main window widget, which is just cointainer for MainMenu widget.
    """
    def __init__(self, screen_size, args):
        super(Window, self).__init__()
        if args.d == "True":
            debug_mode = True
        else:
            debug_mode = False
        width = 800
        height = 600
        self.setFixedSize(width, height)
        self.move((screen_size[2] - width)/2, (screen_size[3] - height)/2 - 20)
        self.setWindowTitle("Duel master - Main menu")
        self.ui = MainMenu(debug_mode, self)
        self.setCentralWidget(self.ui)
        self.show()
