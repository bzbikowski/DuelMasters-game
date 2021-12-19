from src.cards import Card


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
        # TODO: to keep proper layout, min. 5 shields (destoyed or not) are required
        card = self.shields[pos]["card"]
        self.shields[pos] = {}
        return card

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