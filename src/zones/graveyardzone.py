class Graveyardzone():
    def __init__(self, opponent=False, parent=None):
        self.cards = []

    def is_empty(self):
        return len(self.cards) == 0

    def get_last_card(self):
        return self.cards[len(self.cards) - 1]

    def __getitem__(self, index):
        return self.cards[index]

    def __len__(self):
        return len(self.cards)

    def add_card(self, card):
        self.cards.append(card)

    def remove_card(self, card):
        self.cards.remove(card)
