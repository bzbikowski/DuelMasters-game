import logging


class Battlezone():
    # TODO: separate summon sickness from tapping
    # TODO: make battlezone accept infinite cards, not only 5
    def __init__(self, opponent=False, parent=None):
        self._cards = {}
        self.log = logging.getLogger("battlezone")

    def add_card(self, card):
        for i in range(5):
            # Look for free space on the board
            if not self.is_taken(i):
                self._cards[i] = {}
                self._cards[i]["card"] = card
                self._cards[i]["tapped"] = False
                self._cards[i]["shield_count"] = 0
                self._cards[i]["summon_sickness"] = True
                # self._cards[i]["buffs"] = []
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

    def reset_board(self):
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

    def give_effect(self, pos, mode, effect_name, *args):
        args_dict = {key: value for (key, value) in args}
        if mode == "turn":
            args_dict["time"] = 1
            self._cards[pos]["card"].effects.append({effect_name: args_dict})

    def decrement_time_for_effect(self, pos, effect_pos):
        effect_name = list(self._cards[pos]['card'].effects[effect_pos].keys())[0]
        self._cards[pos]['card'].effects[effect_pos][effect_name]["time"] -= 1

    def handle_expired_effects(self):
        for pos, card in self.get_creatures_with_pos():
            delete_list = []
            for effect_pos in range(len(card.effects)):
                effect = card.effects[effect_pos]
                if "time" in list(effect.values())[0] and list(effect.values())[0]["time"] == 0:
                    delete_list.append(effect_pos)
            for delete_pos in sorted(delete_list, reverse=True): # From the latest effect to newest
                self._cards[pos]['card'].effects.pop(delete_pos)

    def get_available_blockers(self):
        blocker_list = []
        for creature_pos, creature_card in self.get_creatures_with_pos():
            for effect in creature_card.effects:
                if "blocker" in effect:
                    if effect["blocker"]["mode"] == "all":
                        blocker_list.append(creature_pos)
        return blocker_list

    def __getitem__(self, index):
        return self._cards[index]["card"]

    def __len__(self):
        return len(self._cards.keys())

    def __iter__(self):
        for card_pos in self._cards.keys():
            if self.is_taken(card_pos):
                self.log.debug(f"{card_pos} - {self._cards[card_pos]['card'].name}")
                yield self._cards[card_pos]["card"]
            else:
                self.log.debug(f"{card_pos} - free")