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
    def __init__(self, opponent=False, parent=None):
        self.cards = []

    def add_card(self, card):
        for i in range(5):
            # Look for free space on the board
            if not self.is_taken(i):
                self.cards.append(card)
                return i
        return -1

    def is_taken(self, pos):
        try:
            self.cards[pos]
        except IndexError as err:
            return False
        else:
            return True

    def remove_card(self, pos):
        return self.cards.pop(pos)

    def __getitem__(self, index):
        return self.cards[index]

    def __len__(self):
        return len(self.cards)

class Manazone():
    def __init__(self, opponent=False, parent=None):
        # TODO: add tapping and locking
        self.cards = []
        self.weights = [0, 0, 0, 0, 0]
        self.dict_civ = {"Light": 0, "Nature": 1, "Darkness": 2, "Fire": 3, "Water": 4}

    def is_selected(self, index):
        # TODO:
        return True

    def is_locked(self, index):
        # TODO:
        return True

    def __getitem__(self, index):
        return self.cards[index]

    def can_be_played(self, index):
        card = self.cards[index]
        sum = 0
        for item in self.weights:
            sum += item
        return sum >= int(card.cost) and not self.weights[self.dict_civ[card.civ]] == 0
    
    def remove_card(self, pos):
        # TODO: remove from tapped mana as well
        # if not card[1]:
        #     self.weights[self.dict_civ[self.find_card(card[0]).civ]] -= 1
        return self.cards.pop(pos)

    def add_card(self, card):
        self.cards.append(card)


class Spellzone():
    def __init__(self, opponent=False, parent=None):
        self.card = None

    def get_card(self):
        return self.card

    def set_card(self, card):
        self.card = card

    def is_taken(self):
        return self.card is not None


