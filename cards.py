import xml.dom.minidom as minidom

class ParseXml:
    def parseFile(self, path):
        cardlist = []
        with minidom.parse(path) as file:
            global_id = 1
            cardsets = file.getElementsByTagName('cardset')
            for cardset in cardsets:
                id = 1
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
                    cardlist.append(Card(id, global_id, setname, cardname, civ, typ, race, cost, power, rarity, rule_text, flavor_text))
                    id += 1
                    global_id += 1
        return cardlist



# struktura do przechowywania informacji o karcie
class Card:
    def __init__(self, set_id, glob_id, set_name, name, civ, typ, race, cost, power, rarity, rules, flavor):
        self.id = set_id
        self.globid = glob_id
        self.name = name
        self.civ = civ
        self.typ = typ
        self.race = race
        self.cost = cost
        self.power = power
        self.rarity = rarity
        self.rules_text = rules
        self.flavor_text = flavor
        self.image = "res//img//" + set_name + '//' + str(self.id) + ".jpg"
