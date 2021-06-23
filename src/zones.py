from random import choice
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

    def __len__(self):
        return len(self.cards)

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

    def discard_random(self):
        pos = choice(range(len(self.cards)))
        self.cards.pop(pos)
        return pos

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


class Battlezone():
    # TODO: separate summon sickness from tapping
    # TODO: make battlezone accept infinite cards, not only 5
    def __init__(self, opponent=False, parent=None):
        self.cards = {}

    def add_card(self, card):
        for i in range(5):
            # Look for free space on the board
            if not self.is_taken(i):
                self.cards[i] = {}
                self.cards[i]["card"] = card
                self.cards[i]["tapped"] = False
                self.cards[i]["shield_count"] = 0
                self.cards[i]["summon_sickness"] = True
                return i
        return -1

    def is_taken(self, pos):
        try:
            self.cards[pos]["card"]
        except KeyError as err:
            return False
        else:
            return True

    def is_tapped(self, pos):
        return self.cards[pos]["tapped"]

    def set_untapped(self, pos):
        self.cards[pos]["tapped"] = False

    def set_tapped(self, pos):
        self.cards[pos]["tapped"] = True

    def has_effect(self, effect_name, pos):
        for effect in self.cards[pos]["card"].effects:
            if effect_name in effect.keys():
                return True
        return False

    def remove_card(self, pos):
        # TODO: to keep proper layout, min. 5 spaces (empty or not) are required
        card = self.cards[pos]["card"]
        self.cards[pos] = {}
        return card

    def reset_shield_count(self):
        for pos in self.cards.keys():
            if self.is_taken(pos):
                self.cards[pos]["tapped"] = False
                self.cards[pos]["summon_sickness"] = False
                if "shieldbreaker" in self.cards[pos]["card"].effects:
                    self.cards[pos]["shield_count"] = self.cards[pos]["card"].effects["shieldbreaker"]["count"]
                elif "notattacking" in self.cards[pos]["card"].effects:
                    if self.cards[pos]["card"].effects["not_attacking"]["mode"] in ["all", "player"]:
                        self.cards[pos]["shield_count"] = 0
                    else:
                        self.cards[pos]["shield_count"] = 1
                else:
                    self.cards[pos]["shield_count"] = 1

    def set_shield_count(self, pos, count):
        self.cards[pos]["shield_count"] = count

    def get_shield_count(self, pos):
        return self.cards[pos]["shield_count"]

    def has_summon_sickness(self, pos):
        return self.cards[pos]["summon_sickness"]

    def __getitem__(self, index):
        return self.cards[index]["card"]

    def __len__(self):
        return len(self.cards.keys())

    def __iter__(self):
        for card_pos in self.cards.keys():
            yield self.cards[card_pos]["card"]

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
        sum = 0
        for item in self.weights:
            sum += item
        return sum >= int(card.cost) and not self.weights[self.dict_civ[card.civ]] == 0

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


