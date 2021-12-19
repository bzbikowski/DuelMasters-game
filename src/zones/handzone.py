from random import choice
from src.cards import Card


class Handzone():
    def __init__(self, opponent=False, parent=None):
        self.cards = []

    def is_hidden(self, index):
        pass

    def add_card(self, card):
        self.cards.append(card)

    def add_placeholder(self):
        self.cards.append(Card(set_id=-1))

    def remove_card(self, pos):
        return self.cards.pop(pos)

    def discard_random(self):
        pos = choice(range(len(self.cards)))
        self.cards.pop(pos)
        return pos

    def __getitem__(self, index):
        return self.cards[index]

    def __len__(self):
        return len(self.cards)