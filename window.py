from PyQt5.QtWidgets import QMainWindow, QApplication
from menu import MainMenu
import sys


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


if __name__ == "__main__":
    app = QApplication(sys.argv)
    size = app.desktop().screenGeometry().getRect()
    qapp = Window(size)
    qapp.show()
    sys.exit(app.exec_())