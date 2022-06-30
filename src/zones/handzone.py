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
        # Remove by position on the hand and return card
        return self.cards.pop(pos)

    def remove_card_by_id(self, card):
        # Remove by id of the card
        self.cards.remove(card)

    def return_random(self):
        pos = choice(range(len(self.cards)))
        return pos

    def __getitem__(self, index):
        return self.cards[index]

    def __len__(self):
        return len(self.cards)