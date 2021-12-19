class Spellzone():
    def __init__(self, opponent=False, parent=None):
        self.card = None

    def get_card(self):
        return self.card

    def set_card(self, card):
        self.card = card

    def is_taken(self):
        # Return true, is field is taken
        return self.card is not None

    def remove_card(self):
        card = self.card
        self.card = None
        return card