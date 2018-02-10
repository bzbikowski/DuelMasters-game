"""
Wiadomości wysyłane do przeciwnika
0 - przeciwnik wygrał
1 - przeciwnik zaczyna
2 - koniec mojej tury
3 - ja dobieram kartę
4,x,y - ja zagrywam kartę o id x na miejscu y na pole bitwy
5,v,x,y - gracz v podnosi kartę z pól x z miejsca y do ręki
          v - 0/1 - przeciwnik/ty
          x - 0/1 - mana/pole bitwy
6,v,x,y - gracz v podnosi kartę z pól x z miejsca y na cmentarz
          v - 0/1 - przeciwnik/ty
          x - 0/1 - mana/pole bitwy
7,x - ja dodaję kartę x z ręki na mane
8,x,y - ja dodaję kartę x z reki na tarczę y
9,x,y - ja tapuje/odtapuje manę
        x - 0/1 - odtapuje/tapuje
        y - pozycja karty na manie
10,x - ja zaglądam w swoją tarczę na pozycji x
11,x,y - ja zaglądam w twoją tarczę/kartę z reki na pozycji y
        x - 0/1 - ręka/tarcza
12,x,y - (info) ja atakuje swoją kartą x twoją kartę y na polu bitwy
13,x - ja niszcze ci tarczę na pozycji x
"""


class Controller:
    def __init__(self, module):
        self.master = module

    def received_message(self, msg):
        command = int(msg[:2], base=16)
        msg = msg[2:]
        if command == 0:
            # 0 - wygrałeś
            self.master.win()
        elif command == 1:
            # 1 - zaczynasz grę
            self.master.turn_states(0)
        elif command == 2:
            # 2 - początek twojej tury
            self.master.turn_states(1)
        elif command == 3:
            # 3 - przeciwnik dobrał kartę
            self.master.opp_hand.append(-1)
        elif command == 4:
            # 4,x,y - przeciwnik gra kartę o id x na miejscu y na pole bitwy
            c_id = int(msg[:2], base=16)
            c_pos = int(msg[2:4], base=16)
            self.master.opp_bfield[c_pos] = c_id
        elif command == 5:
            # 5,v,x,y - gracz v podnosi kartę z pól x z miejsca y do ręki
            # v - 0/1 - ty/przeciwnik
            # x - 0/1 - mana/pole bitwy
            c_player = int(msg[:2], base=16)
            c_space = int(msg[2:4], base=16)
            c_pos = int(msg[4:6], base=16)
            if c_player == 0:
                if c_space == 0:
                    self.master.hand.append(self.master.mana[c_pos][0])
                    self.master.mana.pop(c_pos)
                elif c_space == 1:
                    self.master.hand.append(self.master.bfield[c_pos])
                    self.master.bfield[c_pos] = -1
            elif c_player == 1:
                if c_space == 0:
                    self.master.opp_mana.pop(c_pos)
                    self.master.opp_hand.append(-1)
                elif c_space == 1:
                    self.master.opp_bfield[c_pos] = -1
                    self.master.opp_hand.append(-1)

