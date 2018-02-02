from PyQt5.QtWidgets import QWidget, QPushButton, QGridLayout, QFileDialog
from game import Game
from manager import DeckManager
import sys


class MainMenu(QWidget):
    def __init__(self, parent=None):
        super(MainMenu, self).__init__(parent)
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
        
    def new_game(self):
        if len(self.deck) >= 40:
            self.game = Game(self.deck, self)
            self.game.show()
            self.parent.hide()
        else:
            print("Za malo kart w decku")

    def load_deck(self):
        file = QFileDialog().getOpenFileName(self, "Load deck", "", "Text files (*.txt)")
        if not file:
            return
        self.deck = []
        with open(file[0], "r") as f:
            for line in f.readlines():
                number = int(line.split()[0])
                self.deck.append(number)
        
    def deck_window(self):
        self.window = DeckManager(self)
        self.window.show()
        self.parent.hide()

    def show_window(self):
        self.parent.show()
        
    @staticmethod
    def exit_app():
        sys.exit(0)