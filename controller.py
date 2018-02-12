
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
        elif command == 6:
            # 6,v,x,y - gracz v podnosi kartę z pól x z miejsca y na cmentarz
            # v - 0/1 - ty/przeciwnik
            # x - 0/1 - mana/pole bitwy
            c_player = int(msg[:2], base=16)
            c_space = int(msg[2:4], base=16)
            c_pos = int(msg[4:6], base=16)
            if c_player == 0:
                if c_space == 0:
                    self.master.graveyard.append(self.master.mana[c_pos][0])
                    self.master.mana.pop(c_pos)
                elif c_space == 1:
                    self.master.graveyard.append(self.master.bfield[c_pos])
                    self.master.bfield[c_pos] = -1
            elif c_player == 1:
                if c_space == 0:
                    card = self.master.opp_mana.pop(c_pos)
                    self.master.opp_graveyard.append(card)
                elif c_space == 1:
                    self.master.opp_graveyard.append(self.master.opp_bfield[c_pos])
                    self.master.opp_bfield[c_pos] = -1
        elif command == 7:
            # 7,x - przeciwnik dodaję kartę x z ręki na mane
            c_id = int(msg[:2], base=16)
            self.master.opp_mana.append([c_id, False])
            self.master.opp_hand.pop(0)
        elif command == 8:
            # 8,x,y - przeciwnik dodaję kartę x z reki na tarczę y
            c_id = int(msg[:2], base=16)
            c_pos = int(msg[2:4], base=16)
            self.master.opp_shields[c_pos] = True
            self.master.opp_hand.pop(0)
            print("Card {} as shield...".format(c_id))
        elif command == 9:
            # 9,x,y - ja tapuje/odtapuje manę
            # x - 0/1 - odtapuje/tapuje
            # y - pozycja karty na manie
            c_tap = bool(int(msg[:2]))
            c_pos = int(msg[2:4], base=16)
            self.master.opp_mana[c_pos][1] = c_tap
        elif command == 10:
            # 10,x - przeciwnik zagląda w swoją tarczę na pozycji x
            c_pos = int(msg[:2], base=16)
            print("Opponent is peeking at his no {} shield.".format(c_pos))
        elif command == 11:
            # 11,x,y - przeciwnik zagląda w moją tarczę/kartę z reki na pozycji y
            # x - 0/1 - ręka/tarcza
            c_space = bool(int(msg[:2]))
            c_pos = int(msg[2:4], base=16)
            if c_space:
                card_id = self.master.shields[c_pos]
            else:
                card_id = self.master.hand[c_pos]
            self.master.send_message(111, card_id)
        elif command == 12:
            # 12,x,y - (info) przeciwnik atakuje swoją kartą x moją kartę y na polu bitwy
            c_opp_id = int(msg[:2], base=16)
            c_my_id = int(msg[2:4], base=16)
            print("Your card {} was attacked by opponent creature {}".format(c_my_id, c_opp_id))
        elif command == 13:
            # 13,x - ja niszcze ci tarczę na pozycji x
            c_pos = int(msg[:2], base=16)
            # pokaż tarczę i jeśli jest shield triggerem to zdecyduj co z nią zrobić
            pass
            print("Opponent attacked your shield at posision {}".format(c_pos))










