
class Controller:
    """
    Class which decode received msg into actions
    Todo: change print to logs
    """
    def __init__(self, module):
        """
        Set class to control
        """
        self.master = module

    def received_message(self, msg):
        """
        Decode message, split into values and run the commands
        """
        command = int(msg[:2], base=16)
        msg = msg[2:]
        print("CONTROLLER - COMMAND: " + str(command))
        print("CONTROLLER - MSG: " + str(msg))
        if command == 0:
            # 0 - you win
            # self.master.win()
            # 0 - opponent start the game
            self.master.add_log("Opponent starts the game.")
        elif command == 1:
            # 1 - you start the game
            self.master.add_log("You start the game! Your turn.")
            self.master.turn_states(0)
        elif command == 2:
            # 2 - start of your turn
            self.master.add_log("Your turn.")
            self.master.turn_states(1)
        elif command == 3:
            # 3 - opponent draws a card
            self.master.add_log("Opponent draw a card")
            self.master.opp_hand.append(-1)
        elif command == 4:
            # 4,x,y - opponent plays a card with x id on y spot on gameboard
            c_id = int(msg[:2], base=16)
            c_pos = int(msg[2:4], base=16)
            print("CARD ID: " + str(c_id))
            print("CARD POS: " + str(c_pos))
            self.master.add_log("Opponent played a card")
            self.master.opp_bfield[c_pos] = c_id
        elif command == 5:
            # 5,v,x,y - player v picks up card from x space from y spot to his hand
            # v - 0/1 - you/opponent
            # x - 0/1 - mana/battlefield
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
            # 6,v,x,y - player v puts card from x space from y spot to his graveyard
            # v - 0/1 - you/opponent
            # x - 0/1 - mana/battlefield
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
            # 7,x - opponent adds card x from his hand to mana
            c_id = int(msg[:2], base=16)
            self.master.opp_mana.append([c_id, False])
            self.master.opp_hand.pop(0)
        elif command == 8:
            # 8,x,y - opponent adds card x from his hand to y shield
            c_id = int(msg[:2], base=16)
            c_pos = int(msg[2:4], base=16)
            self.master.opp_shields[c_pos] = True
            self.master.opp_hand.pop(0)
            print("Card {} as shield...".format(c_id))
        elif command == 9:
            # 9,x,y - I tap/untap card on y spot in mana zone
            # x - 0/1 - tap/untap
            c_tap = bool(int(msg[:2]))
            c_pos = int(msg[2:4], base=16)
            self.master.opp_mana[c_pos][1] = c_tap
        elif command == 10:
            # 10,x - (info) opponent looks under his shield on x spot
            c_pos = int(msg[:2], base=16)
            print("Opponent is peeking at his no {} shield.".format(c_pos))
        elif command == 11:
            # 11,x,y - opponent looks under my shield/card on hand on y spot
            # x - 0/1 - hand/shield
            c_space = bool(int(msg[:2]))
            c_pos = int(msg[2:4], base=16)
            if c_space:
                card_id = self.master.shields[c_pos]
            else:
                card_id = self.master.hand[c_pos]
            # todo 111 command
            self.master.send_message(111, card_id)
        elif command == 12:
            # 12,x,y - (info) opponent attacks your x card with his y card on the battlefield
            c_opp_id = int(msg[:2], base=16)
            c_my_id = int(msg[2:4], base=16)
            print("Your card {} was attacked by opponent creature {}".format(c_my_id, c_opp_id))
        elif command == 13:
            # 13,x - opponent destroys your shield on x spot
            c_pos = int(msg[:2], base=16)
            # todo show a card, if shield trigger do something
            pass
            print("Opponent attacked your shield at posision {}".format(c_pos))










