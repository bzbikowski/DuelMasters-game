from src.cards import Card

class Graveyardzone():
    def __init__(self, opponent=False, parent=None):
        self.cards = []

    def is_empty(self):
        return len(self.cards) == 0

    def get_last_card(self):
        return self.cards[len(self.cards) - 1]

    def __getitem__(self, index):
        return self.cards[index]

    def add_card(self, card):
        self.cards.append(card)

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

    def __getitem__(self, index):
        return self.cards[index]

    def __len__(self):
        return len(self.cards)

class Shieldzone():
    def __init__(self, opponent=False, parent=None):
        self.shields = {0: {}, 1: {}, 2: {}, 3: {}, 4: {}}

    def add_shield(self, card):
        index = 0
        while index <= 40:
            if not self.is_shield_exists(index):
                self.shields[index] = {}
                self.shields[index]["card"] = card
                self.shields[index]["visible"] = False
                return index
            index += 1
        print("ERROR: Unexpected add_shield incpetion")
        exit(1)

    def add_placeholder(self):
        index = 0
        while index <= 40:
            if not self.is_shield_exists(index):
                self.shields[index] = {}
                self.shields[index]["card"] = Card(set_id=-1)
                self.shields[index]["visible"] = False
                return index
            index += 1
        print("ERROR: Unexpected add_shield incpetion")
        exit(1)

    def remove_shield(self, pos):
        return self.shields.pop(pos)["card"]

    def __getitem__(self, index):
        return self.shields[index]["card"]

    def __len__(self):
        return len(self.shields.keys())

    def is_shield_exists(self, pos):
        # Return true if shield exists
        try:
            self.shields[pos]["card"]
        except KeyError as err:
            return False
        return True

    def is_shield_visible(self, pos):
        # Return true if shield is face up
        try:
            return self.shields[pos]["visible"]
        except KeyError as err:
            print(f"ERROR: {err}")
            exit(1)

    def set_shield_visible(self, pos):
        self.shields[pos]["visible"] = True


class Battlezone():
    # TODO: add battlezone tapping
    # TODO: if shieldbreaker, card should have multiple attacks toward shields
    # TODO: make battlezone accept infinite cards, not only 5
    def __init__(self, opponent=False, parent=None):
        self.cards = {}

    def add_card(self, card):
        for i in range(5):
            # Look for free space on the board
            if not self.is_taken(i):
                self.cards[i] = {}
                self.cards[i]["card"] = card
                return i
        return -1

    def is_taken(self, pos):
        try:
            self.cards[pos]["card"]
        except KeyError as err:
            return False
        else:
            return True

    def remove_card(self, pos):
        return self.cards.pop(pos)["card"]

    def __getitem__(self, index):
        return self.cards[index]["card"]

    def __len__(self):
        return len(self.cards.keys())

class Manazone():
    def __init__(self, opponent=False, parent=None):
        self.cards = []
        self.weights = [0, 0, 0, 0, 0]
        self.dict_civ = {"Light": 0, "Nature": 1, "Darkness": 2, "Fire": 3, "Water": 4}

    def __getitem__(self, index):
        return self.cards[index]["card"]

    def __len__(self):
        return len(self.cards)

    def is_tapped(self, index):
        return self.cards[index]["tapped"]

    def is_locked(self, index):
        return self.cards[index]["locked"]

    def can_be_played(self, card):
        print(f"WEIGHTS: {str(self.weights)}")
        print(f"CARD COST: {card.cost}")
        sum = 0
        for item in self.weights:
            sum += item
        return sum >= int(card.cost) and not self.weights[self.dict_civ[card.civ]] == 0
    
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

class Spellzone():
    def __init__(self, opponent=False, parent=None):
        self.card = None

    def get_card(self):
        return self.card

    def set_card(self, card):
        self.card = card

    def is_taken(self):
        return self.card is not None

    def remove_card(self):
        self.card = None


