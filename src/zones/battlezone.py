class Battlezone():
    # TODO: separate summon sickness from tapping
    # TODO: make battlezone accept infinite cards, not only 5
    def __init__(self, opponent=False, parent=None):
        self._cards = {}

    def add_card(self, card):
        for i in range(5):
            # Look for free space on the board
            if not self.is_taken(i):
                self._cards[i] = {}
                self._cards[i]["card"] = card
                self._cards[i]["tapped"] = False
                self._cards[i]["shield_count"] = 0
                self._cards[i]["summon_sickness"] = True
                return i
        return -1

    def is_taken(self, pos):
        try:
            self._cards[pos]["card"]
        except KeyError as err:
            return False
        else:
            return True

    def is_tapped(self, pos):
        return self._cards[pos]["tapped"]

    def set_untapped(self, pos):
        self._cards[pos]["tapped"] = False

    def set_tapped(self, pos):
        self._cards[pos]["tapped"] = True

    def has_effect(self, effect_name, pos):
        for effect in self._cards[pos]["card"].effects:
            if effect_name in effect.keys():
                return True
        return False

    def remove_card(self, pos):
        # TODO: to keep proper layout, min. 5 spaces (empty or not) are required
        card = self._cards[pos]["card"]
        self._cards[pos] = {}
        return card

    def reset_shield_count(self):
        for pos in self._cards.keys():
            if self.is_taken(pos):
                self._cards[pos]["tapped"] = False
                self._cards[pos]["summon_sickness"] = False
                if "shieldbreaker" in self._cards[pos]["card"].effects:
                    self._cards[pos]["shield_count"] = int(self._cards[pos]["card"].effects["shieldbreaker"]["count"])
                elif "notattacking" in self._cards[pos]["card"].effects:
                    if self._cards[pos]["card"].effects["not_attacking"]["mode"] in ["all", "player"]:
                        self._cards[pos]["shield_count"] = 0
                    else:
                        self._cards[pos]["shield_count"] = 1
                else:
                    self._cards[pos]["shield_count"] = 1

    def set_shield_count(self, pos, count):
        self._cards[pos]["shield_count"] = count

    def get_shield_count(self, pos):
        return self._cards[pos]["shield_count"]

    def has_summon_sickness(self, pos):
        return self._cards[pos]["summon_sickness"]

    def get_creatures_with_pos(self):
        # card with pos
        for card_pos in self._cards.keys():
            if self.is_taken(card_pos):
                yield card_pos, self._cards[card_pos]["card"]

    def __getitem__(self, index):
        return self._cards[index]["card"]

    def __len__(self):
        return len(self._cards.keys())

    def __iter__(self):
        for card_pos in self._cards.keys():
            if self.is_taken(card_pos):
                yield self._cards[card_pos]["card"]