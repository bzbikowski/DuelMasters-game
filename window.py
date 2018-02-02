from PyQt5.QtWidgets import QMainWindow
from menu import MainMenu


class Window(QMainWindow):
    def __init__(self, screen_size):
        super(Window, self).__init__()
        width = 800
        height = 600
        self.setFixedSize(width, height)
        self.move((screen_size[2] - width)/2, (screen_size[3] - height)/2 - 20)
        self.setWindowTitle("Duel master - Main menu")
        self.ui = MainMenu(self)
        self.setCentralWidget(self.ui)
        self.show()
