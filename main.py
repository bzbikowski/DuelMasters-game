from PyQt5.QtWidgets import QApplication
from src.window import Window
import argparse
import sys


def process_args():
    """
    Parse agruments from command line into the program.
    Args:
    debug | -d | --debug - enable program in debug mode, all messages, warnings and errors will be logged to text file.
    help | -h | --help - print to console help message
    """
    parser = argparse.ArgumentParser(prog="Duel Masters Game")
    parser.add_argument("-d", "--debug", action="store", default="False", help="enable/disable debug mode")
    parsed_args, unparsed_args = parser.parse_known_args()
    return parsed_args, unparsed_args


if __name__ == "__main__":
    parsed_args, unparsed_args = process_args()
    qt_args = sys.argv[:1] + unparsed_args
    app = QApplication(qt_args)
    size = app.desktop().screenGeometry().getRect()[2:4]
    qapp = Window(size, parsed_args)
    qapp.show()
    sys.exit(app.exec_())