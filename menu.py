from PyQt5.QtWidgets import QWidget, QPushButton
from game import Game
from manager import DeckManager
import sys

class MainMenu(QWidget):
    def __init__(self, parent=None):
        super(MainMenu, self).__init__(parent)
        self.deck = []
        game_button = QPushButton("New game", self)
        game_button.move(100, 100)
        game_button.setFixedSize(200, 140)
        game_button.clicked.connect(self.new_game)
        
        deck_button = QPushButton("Deck manager", self)
        deck_button.move(100, 300)
        deck_button.setFixedSize(200, 140)
        deck_button.clicked.connect(self.deck_window)
        
        exit_button = QPushButton("Exit app", self)
        exit_button.move(400, 100)
        exit_button.setFixedSize(200, 140)
        exit_button.clicked.connect(self.exit_app)
        
    def new_game(self):
        if len(self.deck) >= 40:
            self.game = Game(self.deck, self)
            self.game.show()
        else:
            print("Za malo kart w decku")
        
    def deck_window(self):
        self.window = DeckManager(self)
        self.window.show()
        
    def exit_app(self):
        sys.exit(0)
        