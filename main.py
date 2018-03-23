from PyQt5.QtWidgets import QApplication
from window import Window
import argparse
import sys


def process_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--d", "--debug", action="store")
    parsed_args, unparsed_args = parser.parse_known_args()
    return parsed_args, unparsed_args


if __name__ == "__main__":
    parsed_args, unparsed_args = process_args()
    qt_args = sys.argv[:1] + unparsed_args
    app = QApplication(qt_args)
    size = app.desktop().screenGeometry().getRect()
    qapp = Window(size, parsed_args)
    qapp.show()
    sys.exit(app.exec_())