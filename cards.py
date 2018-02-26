import xml.dom.minidom as minidom


class ParseXml:
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
                    cardlist.append(Card(id, global_id, setname, cardname, civ, typ, race, cost, power, rarity, rule_text, flavor_text, [effect_names, effect_dicts]))
                    id += 1
                    global_id += 1
        return cardlist


class Card:
    def __init__(self, set_id, glob_id, set_name, name, civ, typ, race, cost, power, rarity, rules, flavor, effect):
        self.id = set_id
        self.globid = glob_id
        self.name = name
        self.civ = civ
        self.typ = typ
        self.race = race
        self.cost = cost
        self.power = power
        self.rarity = rarity
        self.effect = effect
        self.rules_text = rules
        self.flavor_text = flavor
        self.image = "res//img//" + set_name + '//' + str(self.id) + "//" + "low.jpg"
        self.prev = "res//img//" + set_name + '//' + str(self.id) + "//" + "med.jpg"
        self.info = "res//img//" + set_name + '//' + str(self.id) + "//" + "high.jpg"
