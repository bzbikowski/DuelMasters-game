from PyQt5.QtWidgets import QMainWindow, QApplication
from menu import MainMenu
import sys
#import win32api


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.width = 800
        self.height = 600
        #screen_width = win32api.GetSystemMetrics(0)
        #screen_height = win32api.GetSystemMetrics(1)
        self.setFixedSize(self.width, self.height)
        #self.move((screen_width - self.width)/2, (screen_height - self.height)/2 - 20)
        self.setWindowTitle("Duel master - Main menu")
        self.ui = MainMenu(self)
        self.setCentralWidget(self.ui)
        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    qapp = Window()
    qapp.show()
    sys.exit(app.exec_())