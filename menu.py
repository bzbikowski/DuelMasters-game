from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout, QFileDialog, QMessageBox
from game import Game
from manager import DeckManager
import sys
import logging
import datetime


class MainMenu(QWidget):
    """
    Widget, where all the things connected with start screen will be putted.
    """
    def __init__(self, debug_mode, parent=None):
        """
        Init all widgets and layout for the menu.
        """
        super(MainMenu, self).__init__(parent)
        self.is_debug_mode = debug_mode

        self.game = None
        self.log = None
        self.window = None
        self.deck = []
        self.parent = parent
        self.main_layout = QGridLayout(self)

        game_button = QPushButton("New game", self)
        game_button.clicked.connect(self.new_game)
        self.main_layout.addWidget(game_button, 0, 0)

        deck_button = QPushButton("Load deck", self)
        deck_button.clicked.connect(self.load_deck)
        self.main_layout.addWidget(deck_button, 0, 1)
        
        manager_button = QPushButton("Deck manager", self)
        manager_button.clicked.connect(self.deck_window)
        self.main_layout.addWidget(manager_button, 1, 0)
        
        exit_button = QPushButton("Exit app", self)
        exit_button.clicked.connect(self.exit_app)
        self.main_layout.addWidget(exit_button, 1, 1)

        self.setup_logger(debug_mode)

    def setup_logger(self, dm):
        self.log = logging.getLogger("dm_game")
        if dm:
            self.log.setLevel(logging.DEBUG)
        else:
            self.log.setLevel(logging.DEBUG)
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
            self.game = Game(self.deck, self.is_debug_mode, self)
            self.game.show()
            self.parent.hide()
        else:
            self.log.warning("Deck incomplete.")
            _ = QMessageBox.information(self, "Information", "Your deck is incomplete",
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
                    _ = QMessageBox.information(self, "Information", "This text file is corrupted.",
                                                QMessageBox.Ok, QMessageBox.NoButton)
                    self.deck = []
                    self.log.debug("Deck load failed")
                    return
                self.deck.append(number)
        self.log.debug("Deck load success")
        
    def deck_window(self):
        """
        Open deck creator.
        """
        self.log.debug("Button editor clicked")
        self.window = DeckManager(self, self.deck)
        self.log.debug("Class DeckManager created")
        self.window.show()
        self.parent.hide()

    def show_window(self):
        self.parent.show()
        
    @staticmethod
    def exit_app():
        sys.exit(0)