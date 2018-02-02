from PyQt5.QtWidgets import QApplication
from window import Window
import sys

if __name__ == "__main__":
    app = QApplication(sys.argv)
    size = app.desktop().screenGeometry().getRect()
    qapp = Window(size)
    qapp.show()
    sys.exit(app.exec_())