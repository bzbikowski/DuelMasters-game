import argparse
import sys

from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QGuiApplication

from src.window import Window


def process_args():
    """
    Parse agruments from command line into the program.
    Args:
    debug | -d | --debug - enable program in debug mode, all messages, warnings and errors will be logged to text file.
    help | -h | --help - print to console help message
    """
    parser = argparse.ArgumentParser(prog="Duel Masters Game")
    parser.add_argument("-d", "--debug", action="store", default="True", help="enable/disable debug mode")
    parsed_args, unparsed_args = parser.parse_known_args()
    return parsed_args, unparsed_args


if __name__ == "__main__":
    parsed_args, unparsed_args = process_args()
    qt_args = sys.argv[:1] + unparsed_args
    app = QApplication(qt_args)
    window = Window(parsed_args)
    window.show()
    sys.exit(app.exec())
