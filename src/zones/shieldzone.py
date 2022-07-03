import logging

from src.cards import Card


class Shieldzone():
    def __init__(self, opponent=False, parent=None):
        self.shields = {0: {}, 1: {}, 2: {}, 3: {}, 4: {}}

        self.log = logging.getLogger("shieldzone")

    def add_shield(self, card):
        index = 0
        while index <= 40: # safety measures
            if not self.is_shield_exists(index):
                self.shields[index] = {}
                self.shields[index]["card"] = card
                self.shields[index]["visible"] = False
                return index
            index += 1
        self.log.error("ERROR: Unexpected add_shield incpetion")
        exit(1)

    def add_placeholder(self, pos=None): # TODO: test it
        if pos is not None:
                self.shields[pos] = {}
                self.shields[pos]["card"] = Card(set_id=-1)
                self.shields[pos]["visible"] = False
        else:
            index = 0
            while index <= 40: # safety measures
                if not self.is_shield_exists(index):
                    self.shields[index] = {}
                    self.shields[index]["card"] = Card(set_id=-1)
                    self.shields[index]["visible"] = False
                    return index
                index += 1
            self.log.error("ERROR: Unexpected add_shield incpetion")
            exit(1)

    def get_count(self):
        count = 0
        for index in range(len(self.shields)):
            if self.is_shield_exists(index):
                count += 1
        return count

    def remove_shield(self, pos):
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
            self.log.error(f"ERROR: {err}")
            exit(1)

    def set_shield_visible(self, pos):
        self.shields[pos]["visible"] = True