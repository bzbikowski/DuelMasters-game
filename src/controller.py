import logging


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
        self.log = logging.getLogger("dm_game")

    def received_message(self, msg):
        """
        Decode message, split into values and run the commands
        """
        command = int(msg[:2], base=16)
        msg = msg[2:]
        self.log.debug("CONTROLLER - RECEIVED COMMAND: " + str(command))
        self.log.debug("CONTROLLER - MSG: " + str(msg))
        if command == 0:
            # 0 - you win
            # self.master.win()
            # 0 - opponent start the game
            self.master.add_log("Opponent starts the game.")
        elif command == 1:
            # 1 - you start the game
            self.master.add_log("You start the game! Your turn.")
            self.master.new_round()
        elif command == 2:
            # 2 - start of your turn
            self.master.add_log("Your turn.")
            self.master.new_round(True)
        elif command == 3:
            # 3 - opponent draws a card
            self.master.opp_hand.add_placeholder()
            self.master.add_log("Opponent draw a card.")
        elif command == 4:
            # 4,x,y - opponent plays a card with x id on y spot on gameboard
            c_id = int(msg[:2], base=16)
            c_pos = int(msg[2:4], base=16)
            card = self.master.database.get_card(c_id)
            if card.card_type == "Spell":
                self.master.opp_sfield.set_card(card)
            else:
                self.master.opp_bfield.add_card(card)
            self.master.opp_hand.remove_card(0)
            self.master.add_log(f"Opponent played a card {card.name}.")
        elif command == 5:
            # 5,v,x,y - player v picks up card from x space from y spot to his hand
            # v - 0/1 - you/opponent
            # x - 0/1 - mana/battlefield
            c_player = int(msg[:2], base=16)
            c_space = int(msg[2:4], base=16)
            c_pos = int(msg[4:6], base=16)
            if c_player == 0:
                if c_space == 0:
                    card = self.master.mana.remove_card(c_pos)
                    self.master.hand.add_card(card)
                    self.master.add_log(f"You pick up {card.name} from mana zone to your hand.")
                elif c_space == 1:
                    card = self.master.bfield.remove_card(c_pos)
                    self.master.hand.add_card(card)
                    self.master.add_log(f"You pick up {card.name} from battle zone to your hand.")
            elif c_player == 1:
                if c_space == 0:
                    card = self.master.opp_mana.remove_card(c_pos)
                    self.master.opp_hand.add_placeholder()
                    # TODO: add better logging (which card etc.)
                    self.master.add_log(f"Opponent picks up {card.name} from mana to his hand.")
                elif c_space == 1:
                    card = self.master.opp_bfield.remove_card(c_pos)
                    self.master.opp_hand.add_placeholder()
                    # TODO: add better logging (which card etc.)
                    self.master.add_log(f"Opponent picks up {card.name} from battle zone to his hand.")
        elif command == 6:
            # 6,v,x,y - player v puts card from x space from y spot to his graveyard
            # v - 0/1 - you/opponent
            # x - 0/1 - mana/battlefield/hand
            c_player = int(msg[:2], base=16)
            c_space = int(msg[2:4], base=16)
            c_pos = int(msg[4:6], base=16)
            if c_player == 0:
                if c_space == 0:
                    card = self.master.mana.remove_card(c_pos)
                    self.master.graveyard.add_card(card)
                    self.master.add_log(f"Your card {card.name} from mana zone was moved to your graveyard.")
                elif c_space == 1:
                    card = self.master.bfield.remove_card(c_pos)
                    self.master.graveyard.add_card(card)
                    self.master.add_log(f"Your card {card.name} from battle zone was moved to your graveyard.")
                elif c_space == 2:
                    card = self.master.hand.remove_card(c_pos)
                    self.master.graveyard.add_card(card)
                    self.master.send_message(15, card.id)
                    self.master.add_log(f"Your card {card.name} from hand was discarded to your graveyard.")
            elif c_player == 1:
                if c_space == 0:
                    card = self.master.opp_mana.remove_card(c_pos)
                    self.master.opp_graveyard.add_card(card)
                    self.master.add_log(f"Opponent's card {card.name} from mana zone was moved to his graveyard.")
                elif c_space == 1:
                    if c_pos == 5:
                        card = self.master.opp_sfield.remove_card()
                    else:
                        card = self.master.opp_bfield.remove_card(c_pos)
                    self.master.opp_graveyard.add_card(card)
                    self.master.add_log(f"Opponent's card {card.name} from battle zone was moved to his graveyard.")
        elif command == 7:
            # 7,x - opponent adds card x from his hand to mana
            c_id = int(msg[:2], base=16)
            card = self.master.database.get_card(c_id)
            self.master.opp_mana.add_card(card)
            self.master.opp_hand.remove_card(0)
            self.master.add_log(f"Opponent played card {card.name} from his hand to the mana zone")
        elif command == 8:
            # 8,x - opponent adds card from his hand to y shield (face down)
            c_pos = int(msg[0:2], base=16)
            self.master.opp_shields.add_placeholder()
            self.master.opp_hand.remove_card(0)
            self.master.add_log(f"Opponent added card from his hand to shields")
        elif command == 9:
            # 9,x,y - Opponent tap/untap card on y spot in mana zone
            # x - 0/1 - tap/untap
            c_tap = bool(int(msg[:2]))
            c_pos = int(msg[2:4], base=16)
            if c_tap:
                self.master.opp_mana.untap_card(c_pos)
            else:
                self.master.opp_mana.tap_card(c_pos)
        elif command == 10:
            # 10,x - (info) opponent looks under his shield on x spot
            c_pos = int(msg[:2], base=16)
            self.master.add_log(f"Opponent is peeking his {c_pos} shield")
        elif command == 11:
            # 11,x,y - opponent looks under my shield/card on hand on y spot
            # x - 0/1 - hand/shield
            c_space = int(msg[:2])
            c_pos = int(msg[2:4], base=16)
            if c_space == 0:
                card = self.master.hand[c_pos]
                self.master.add_log(f"Opponent is peeking your {c_pos} card in hand")
            elif c_space == 1:
                card = self.master.shields[c_pos]
                self.master.add_log(f"Opponent is peeking your {c_pos} shield")
            # TODO: implement 111 command - return id of the card back to opponent
            self.master.send_message(111, card.id)
        elif command == 111:
            # 111,x - 
            c_id = int(msg[:2], base=16)
            # TODO: split command to separate hand and shield
            # TODO: show in the UI what the card actually is
            self.master.add_log(f"The choosen card is {c_id}")
        elif command == 12:
            # 12,x,y - opponent attacks your x card with his y card on the battlefield
            c_opp_pos = int(msg[:2], base=16)
            c_my_pos = int(msg[2:4], base=16)
            opp_card = self.master.opp_bfield[c_opp_pos]
            my_card = self.master.bfield[c_my_pos]
            self.master.add_log(f"Opponent is attacking your card {my_card.name} with card {opp_card.name}.")
            self.master.creature_attacked(c_opp_pos, c_my_pos)
        elif command == 112:
            # 112,x - returned which card you will attack
            c_pos = int(msg[:2], base=16)
            self.master.attack_creature(c_pos)
        elif command == 13:
            # 13,x,y1,y2,... - opponent attacks your shields with y card
            # x - position of creature on the board
            # ya - a-th shield attacked by this creature
            creature_pos = int(msg[:2], base=16)
            msg = msg[2:]
            shields_pos = []
            while len(msg) > 0:
                shields_pos.append(int(msg[0:2], base=16))
                msg = msg[2:]
            shields_string = ", ".join([str(pos) for pos in shields_pos])
            self.master.add_log(f"Your shields at pos {shields_string} are being attacked by {self.master.opp_bfield[creature_pos].name}.")
            self.master.shields_attacked(creature_pos, shields_pos)
        elif command == 113:
            # 113,x - answer from the opponent, that either he blocks with blocker or shields will be destroyed
            if msg == "":
                # Opponent didn't block shield attack, continue
                self.master.attack_shield()
            else:
                # Oppponent blocked with creature
                self.master.selected_shields = []
                c_pos = int(msg[:2], base=16)
                self.master.attack_creature(c_pos)
        elif command == 14:
            # 14,y1,y2,... - opponent destroys your shields
            # ya - a-th shield
            shields_pos = []
            while len(msg) > 0:
                shields_pos.append(int(msg[0:2], base=16))
                msg = msg[2:]
            self.master.shield_destroyed(shields_pos)
        elif command == 114:
            # 114,x - opponent picked up x shield to his hand
            c_pos = int(msg[:2], base=16)
            self.master.opp_shields.remove_shield(c_pos)
            self.master.opp_hand.add_placeholder()
            self.master.add_log(f"Opponent picked up {c_pos} shield to his hand.")
            self.master.refresh_screen()
        elif command == 214:
            # 214 - opponent ended handling shield attack
            self.master.selected_card = []
            self.master.your_turn = 1
        elif command == 15:
            # 15 - id of the discarded card
            c_id = int(msg[:2], base=16)
            card = self.master.database.get_card(c_id)
            self.master.opp_graveyard.add_card(card)
            self.master.add_log(f"Opponent discarded {card.name}")
            self.master.refresh_screen()
        elif command == 16:
            # 16,v,x,y - x player taps/untaps a y creature
            # v - 0/1 - tap/untap
            # x - 0/1 - you/opponent
            # y - pos
            c_tap = int(msg[:2], base=16)
            c_player = int(msg[2:4], base=16)
            c_pos = int(msg[4:6], base=16)
            if c_tap == 0:
                # Tap
                if c_player == 0:
                    # You
                    self.master.bfield.set_tapped(c_pos)
                    self.master.add_log(f"Your creature at pos {c_pos} is now tapped.")
                elif c_player == 1:
                    self.master.opp_bfield.set_tapped(c_pos)
                    self.master.add_log(f"Opponent creature at pos {c_pos} is now tapped.")
            if c_tap == 1:
                # Untap
                if c_player == 0:
                    # You
                    self.master.bfield.set_untapped(c_pos)
                    self.master.add_log(f"Your creature at pos {c_pos} is now untapped.")
                elif c_player == 1:
                    self.master.opp_bfield.set_untapped(c_pos)
                    self.master.add_log(f"Opponent creature at pos {c_pos} is now untapped.")
            self.master.refresh_screen()
        elif command == 17:
            # 17,c,s1,p1,s2,p2... - opponent chooses which cards to destroy from the list
            # c - how many creatures to destoy
            # sa - set of a-th card
            # pa - position of a-th card
            target_list = []
            count=int(msg[0:2], base=16)
            msg = msg[2:]
            while len(msg) > 0:
                set=int(msg[0:2], base=16)
                pos=int(msg[2:4], base=16)
                target_list.append((set, pos))
                msg = msg[4:]
            self.master.select_creatures_to_be_destoyed(count, target_list)
        elif command == 117:
            # 117 - opponent choosed cards and his actions ended
            self.master.post_destroy_creatures()

            











