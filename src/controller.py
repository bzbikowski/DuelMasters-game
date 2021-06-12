
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
            self.master.opp_hand.append(-1)
            self.master.add_log("Opponent draw a card.")
        elif command == 4:
            # 4,x,y - opponent plays a card with x id on y spot on gameboard
            c_id = int(msg[:2], base=16)
            c_pos = int(msg[2:4], base=16)
            print(f"COMMAND CARD PLAYED - CARD ID {str(c_id)}, CARD POS: {str(c_pos)}")
            self.master.opp_bfield[c_pos] = c_id
            self.master.add_log("Opponent played a card.")
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
                    self.master.add_log("You pick up card from mana to your hand.")
                elif c_space == 1:
                    self.master.hand.append(self.master.bfield[c_pos])
                    self.master.bfield[c_pos] = -1
                    self.master.add_log("You pick up card from battle zone to your hand.")
            elif c_player == 1:
                if c_space == 0:
                    self.master.opp_mana.pop(c_pos)
                    self.master.opp_hand.append(-1)
                    self.master.add_log("Opponent picks up card from mana to your hand.")
                elif c_space == 1:
                    self.master.opp_bfield[c_pos] = -1
                    self.master.opp_hand.append(-1)
                    self.master.add_log("Opponent picks up card from battle zone to your hand.")
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
                    self.master.add_log("Your card from mana zone was moved to your graveyard.")
                elif c_space == 1:
                    self.master.graveyard.append(self.master.bfield[c_pos])
                    self.master.bfield[c_pos] = -1
                    self.master.add_log("Your card from battle zone was moved to your graveyard.")
            elif c_player == 1:
                if c_space == 0:
                    card = self.master.opp_mana.pop(c_pos)
                    self.master.opp_graveyard.append(card)
                    self.master.add_log("Opponent's card from mana zone was moved to his graveyard.")
                elif c_space == 1:
                    self.master.opp_graveyard.append(self.master.opp_bfield[c_pos])
                    self.master.opp_bfield[c_pos] = -1
                    self.master.add_log("Opponent's card from battle zone was moved to his graveyard.")
        elif command == 7:
            # 7,x - opponent adds card x from his hand to mana
            c_id = int(msg[:2], base=16)
            self.master.opp_mana.append([c_id, True])
            self.master.opp_hand.pop(0)
            self.master.add_log(f"Opponent played card {c_id} from his hand to the mana zone")
        elif command == 8:
            # 8,x,y - opponent adds card x from his hand to y shield (face down)
            c_id = int(msg[:2], base=16)
            c_pos = int(msg[2:4], base=16)
            self.master.opp_shields[c_pos] = True
            self.master.opp_hand.pop(0)
            self.master.add_log(f"Opponent added card from his hand to shields")
        elif command == 9:
            # 9,x,y - I tap/untap card on y spot in mana zone
            # x - 0/1 - tap/untap
            c_tap = bool(int(msg[:2]))
            c_pos = int(msg[2:4], base=16)
            self.master.opp_mana[c_pos][1] = c_tap
            if c_tap == 0:
                self.master.add_log(f"Opponent tapped a card in his mana zone")
            elif c_tap == 1:
                self.master.add_log(f"Opponent untapped a card in his mana zone")
        elif command == 10:
            # 10,x - (info) opponent looks under his shield on x spot
            c_pos = int(msg[:2], base=16)
            self.master.add_log(f"Opponent is peeking his {c_pos} shield")
        elif command == 11:
            # 11,x,y - opponent looks under my shield/card on hand on y spot
            # x - 0/1 - hand/shield
            c_space = int(msg[:2])
            c_pos = int(msg[2:4], base=16)
            if c_space == 1:
                card_id = self.master.shields[c_pos]
                self.master.add_log(f"Opponent is peeking your {c_pos} shield")
            elif c_space == 0:
                card_id = self.master.hand[c_pos]
                self.master.add_log(f"Opponent is peeking your {c_pos} card in hand")
            else:
                print("COMMAND 11 ERROR - WRONG PARAMS")
            # TODO: implement 111 command - return id of the card back to opponent
            self.master.send_message(111, card_id)
        elif command == 12:
            # 12,x,y - (info) opponent attacks your x card with his y card on the battlefield
            c_opp_id = int(msg[:2], base=16)
            c_my_id = int(msg[2:4], base=16)
            self.master.add_log(f"Opponent is attacking your card {c_my_id} with card {c_opp_id}.")
        elif command == 13:
            # 13,x - opponent destroys your shield on x spot
            c_pos = int(msg[:2], base=16)
            self.master.add_log(f"Opponent attacked your shield at posision {c_pos}.")
            self.master.shield_destroyed(c_pos)
        elif command == 111:
            # 111,x - 
            # TODO: check if this command is expected
            c_id = int(msg[:2], base=16)
            # TODO: split command to separate hand and shield
            # TODO: show in the UI what the card actually is
            self.master.add_log(f"The choosen card is {c_id}")
        elif command == 113:
            # 113,x - opponent draw to hand destroyed x shield
            # TODO: check if this command is expected
            c_pos = int(msg[:2], base=16)
            self.master.opp_shields[c_pos] = False
            self.master.opp_hand.append(-1)
            self.master.add_log(f"Opponent picked up shield {c_pos} to his hand.")
            self.master.your_turn = True
        elif command == 213:
            # 213 - return your turn back
            # TODO: check if this command is expected
            self.master.your_turn = 1

            











