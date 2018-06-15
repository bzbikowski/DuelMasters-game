from window import Window
from menu import MainMenu
from game import Game
from connection import Server

if __name__ == "__main__":
    window = Window()
    window.ui.deck = [1 * 40]
    window.ui.new_game()
    window.ui.game.test_for_raspberry()

