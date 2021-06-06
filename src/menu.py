import datetime
import logging
import sys

from PySide2.QtWidgets import QWidget, QPushButton, QGridLayout, QFileDialog, QMessageBox

from src.database import Database
from src.game import Game
from src.manager import DeckManager
from src.ui.ui_menu import Ui_Menu
from src.connection import Connection


class MainMenu(QWidget):
    """
    Widget, where all the things connected with start screen will be putted.
    """
    def __init__(self, debug_mode, parent=None):
        """
        Initialize all widgets and layouts for the menu.
        """
        super(MainMenu, self).__init__(parent)
        self.ui = Ui_Menu()
        self.ui.setupUi(self)
        self.is_debug_mode = debug_mode

        self.game = None
        self.log = None
        self.window = None
        self.deck = []
        self.parent = parent

        self.ui.game_button.clicked.connect(self.new_game)
        self.ui.deck_button.clicked.connect(self.load_deck)
        self.ui.manager_button.clicked.connect(self.deck_window)
        self.ui.exit_button.clicked.connect(self.exit_app)

        self.setup_logger(debug_mode)
        self.database = Database()

    def setup_logger(self, dm):
        import os
        if not os.path.exists('./logs'):
            os.mkdir('./logs')
        self.log = logging.getLogger("dm_game")
        if dm:
            self.log.setLevel(logging.DEBUG)
        else:
            self.log.setLevel(logging.INFO)
        time = datetime.datetime.now()
        terminal = logging.FileHandler('logs/{0}-{1}-{2}_{3}-{4}-{5}.log'.format(time.year, time.month, time.day, time.hour, time.minute, time.second))
        terminal.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        terminal.setFormatter(formatter)
        self.log.addHandler(terminal)
        
    def new_game(self):
        """
        If your deck is completed, run game widget.
        """
        self.log.debug("Button start clicked")
        if len(self.deck) >= 40:
            self.log.info("Game class created")
            self.connection = Connection(self)
            mode = self.connection.exec_()
            if mode == 0:
                self.show_window()
            elif mode in [1, 2]:
                self.game = Game(mode, self.deck, self.database, self.is_debug_mode, self)
                # self.game.show()
                self.parent.hide()
            else:
                print("Weird error")
                sys.exit(99)
        else:
            self.log.warning("Deck incomplete.")
            _ = QMessageBox.information(self, "Information", "Minimum required deck size is 40 cards."
                                                             " Please, add remaining cards in Deck manager section"
                                                             " in main menu. ",
                                        QMessageBox.Ok, QMessageBox.NoButton)

    def load_deck(self):
        """
        Load your deck from txt file.
        """
        self.log.debug("Button load clicked")
        file = QFileDialog().getOpenFileName(self, "Load deck", ".//decks", "Text files (*.txt)")
        if not file or file[0] == "":
            return
        self.log.debug("Trying to load {} file".format(file[0]))
        self.deck = []
        with open(file[0], "r") as f:
            for line in f.readlines():
                try:
                    number = int(line.split()[0])
                except ValueError:
                    _ = QMessageBox.information(self, "Information", "This deck file is corrupted."
                                                                     " Please, create new deck. ",
                                                QMessageBox.Ok, QMessageBox.NoButton)
                    self.deck = []
                    self.log.debug("Deck load failed")
                    return
                self.deck.append(number)
        self.log.debug(f"{file[0]} deck load success")
        
    def deck_window(self):
        """
        Open deck creator.
        """
        self.log.debug("Button editor clicked")
        self.window = DeckManager(self.database, self, self.deck)
        self.log.debug("Class DeckManager created")
        self.window.show()
        self.parent.hide()

    def show_window(self):
        self.parent.show()
        
    @staticmethod
    def exit_app():
        sys.exit(0)
