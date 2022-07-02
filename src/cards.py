import json
import xml.dom.minidom as minidom

from PySide6.QtCore import QFile, QIODevice


class Card:
    """
    Simple class to cointaining all the data about one card
    """
    def __init__(self, set_id=None, glob_id=None, name=None, civ=None, card_type=None, race=None, cost=None, power=None, effect=None, set_name=None):
        """
        :param set_id: identification number of card-set
        :param glob_id: identification number of card in all card-sets
        :param set_name: name of card-set
        :param name: name of card
        :param civ: civilization of card
        :param card_type: type of card (creature, spell etc..)
        :param race: race of card (if creature)
        :param cost: cost of card in mana
        :param power: power of card (if creature)
        :param rarity: rarity of card
        :param effect: effects of the card
        """
        self.id = set_id
        self.globid = glob_id
        self.set_name = set_name
        self.name = name
        self.civ = civ
        self.card_type = card_type
        self.race = race
        self.cost = cost
        self.power = power
        self.effects = effect

    def __eq__(self, other):
        return self.globid == other.globid

    def is_placeholder(self):
        return self.id == -1

    @staticmethod
    def parse_effects(effects):
        json_parse = []
        names, dicts = effects
        for effect in zip(names, dicts):
            eff_d = {effect[0]: effect[1]}
            json_parse.append(eff_d)
        return json_parse, json.dumps({"effects": json_parse})

    @staticmethod
    def load_images(folder_path, set_name, set_id):
        images = {}
        sizes = ["low", "medium", "high"]
        for size in sizes:
            path = f"{folder_path}//{set_name}//{str(set_id)}//{size}.jpg"
            file = QFile(path)
            if not file.open(QIODevice.ReadOnly):
                print(f"ERROR: couldn't open file {path}")
                return
            images[size] = file.readAll()
        return images

    @staticmethod
    def parseFile(path):
        cardlist = []
        with minidom.parse(path) as file:
            global_id = 0
            cardsets = file.getElementsByTagName('cardset')
            for cardset in cardsets:
                id = 0
                if cardset.getAttribute('setname') == 'Base Set':
                    setname = "base_set"
                else:
                    setname = cardset.getAttribute('setname')
                cards = cardset.getElementsByTagName('card')
                for card in cards:
                    cardname = card.getAttribute('name')
                    civ = card.getAttribute('civilization')
                    typ = card.getAttribute('type')
                    race = card.getAttribute('race')
                    cost = card.getAttribute('cost')
                    power = card.getAttribute('power')
                    rarity = card.getAttribute('rarity')
                    col_num = card.getAttribute('collector_number')
                    artist = card.getAttribute('artist')
                    rule = card.getElementsByTagName('rules_text')[0]
                    try:
                        rule_text = rule.firstChild.nodeValue
                    except AttributeError:
                        rule_text = ""
                    flavor = card.getElementsByTagName('flavor_text')[0]
                    try:
                        flavor_text = flavor.firstChild.nodeValue
                    except AttributeError:
                        flavor_text = ""
                    effects = card.getElementsByTagName("effects")[0]
                    r_effects = [item for item in effects.childNodes if item.nodeType == item.ELEMENT_NODE]
                    effect_names = []
                    effect_dicts = []
                    for effect in r_effects:
                        effect_name = effect.nodeName
                        effect_dict = {}
                        for key in effect.attributes.keys():
                            effect_dict[key] = effect.attributes[key].firstChild.nodeValue
                        if effect_name == "give":
                            # Handle give effect
                            give_effects = [item for item in effect.childNodes if item.nodeType == item.ELEMENT_NODE]
                            for give_effect in give_effects:
                                give_effect_name = give_effect.nodeName
                                give_effect_dict = {}
                                for key in give_effect.attributes.keys():
                                    give_effect_dict[key] = give_effect.attributes[key].firstChild.nodeValue
                            effect_dict["effect"] = {give_effect_name: give_effect_dict}
                        effect_dict["time"] = "-"
                        effect_names.append(effect_name)
                        effect_dicts.append(effect_dict)
                    cardlist.append((id, global_id, setname, cardname, civ, typ, race, cost, power, rarity, col_num,
                                         artist, rule_text, flavor_text, [effect_names, effect_dicts]))
                    id += 1
                    global_id += 1
        return cardlist
