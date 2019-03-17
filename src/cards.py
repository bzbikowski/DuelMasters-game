import json
import xml.dom.minidom as minidom

from PySide2.QtCore import QFile, QIODevice


class ParseXml:
    """
    Class which refactor xml data containing informations about cards
    """
    @staticmethod
    def parseFile(path):
        cardlist = []
        with minidom.parse(path) as file:
            global_id = 0
            cardsets = file.getElementsByTagName('cardset')
            for cardset in cardsets:
                id = 0
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
                        effect_names.append(effect_name)
                        effect_dicts.append(effect_dict)
                    cardlist.append(Card(id, global_id, setname, cardname, civ, typ, race, cost, power, rarity, col_num,
                                         artist, rule_text, flavor_text, [effect_names, effect_dicts]))
                    id += 1
                    global_id += 1
        return cardlist


class Card:
    """
    Simple class to cointaining all the data about one card
    """
    def __init__(self, set_id, glob_id, set_name, name, civ, typ, race, cost, power, rarity, col_num,
                 artist, rules, flavor, effect):
        # todo add doc
        self.id = set_id
        self.globid = glob_id
        self.set_name = set_name
        self.name = name
        self.civ = civ
        self.typ = typ
        self.race = race
        self.cost = cost
        self.power = power
        self.rarity = rarity
        self.col_num = col_num
        self.artist = artist
        self.rules_text = rules
        self.flavor_text = flavor
        self.effects, self.effects_json = self.parse_effects(effect)
        self.images = self.load_images(set_name, set_id)

    def parse_effects(self, effects):
        json_parse = []
        names, dicts = effects
        for effect in zip(names, dicts):
            eff_d = {effect[0]: effect[1]}
            json_parse.append(eff_d)
        return json_parse, json.dumps({"effects": json_parse})

    def load_images(self, set_name, set_id):
        images = {}
        sizes = ["low"]
        for size in sizes:
            path = f"res//img//{set_name}//{str(set_id)}//{size}.jpg"
            file = QFile(path)
            if not file.open(QIODevice.ReadOnly):
                return
            images[size] = file.readAll()
        return images
