import logging


class Manazone():
    def __init__(self, opponent=False, parent=None):
        self.cards = []
        self.weights = [0, 0, 0, 0, 0]
        self.dict_civ = {"Light": 0, "Nature": 1, "Darkness": 2, "Fire": 3, "Water": 4}

        self.log = logging.getLogger("dm_game")

    def __getitem__(self, index):
        return self.cards[index]["card"]

    def __len__(self):
        return len(self.cards)

    def is_tapped(self, index):
        return self.cards[index]["tapped"]

    def is_locked(self, index):
        return self.cards[index]["locked"]

    def can_be_played(self, card):
        self.log.debug(f"Can be played: weights {str(self.weights)}, card {card.name}")
        sum = 0
        for item in self.weights:
            sum += item
        return sum == int(card.cost) and not self.weights[self.dict_civ[card.civ]] == 0

    def lock_used_mana(self):
        # TODO: lock only used mana if more cards are tapped in mana
        for pos in range(len(self.cards)):
            if self.cards[pos]["tapped"]:
                self.cards[pos]["locked"] = True
        self.weights = [0, 0, 0, 0, 0]

    def unlock_and_untap(self):
        for pos in range(len(self.cards)):
            self.cards[pos]["tapped"] = False
            self.cards[pos]["locked"] = False
    
    def remove_card(self, pos):
        if self.cards[pos]["tapped"]:
            self.weights[self.dict_civ[self.cards[pos]["card"].civ]] -= 1
        return self.cards.pop(pos)["card"]

    def add_card(self, card):
        self.cards.append({"card": card, "locked": False, "tapped": False})

    def tap_card(self, pos):
        if not self.cards[pos]["locked"]:
            self.weights[self.dict_civ[self.cards[pos]["card"].civ]] += 1
            self.cards[pos]["tapped"] = True

    def untap_card(self, pos):
        if not self.cards[pos]["locked"]:
            self.weights[self.dict_civ[self.cards[pos]["card"].civ]] -= 1
            self.cards[pos]["tapped"] = False