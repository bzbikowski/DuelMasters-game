from PySide6.QtCore import QObject, Slot, Qt
from PySide6.QtGui import QCursor, QTransform, QPixmap, QAction
from PySide6.QtWidgets import QGraphicsScene, QGraphicsPixmapItem, QMenu, QWidget


class CardView(QGraphicsPixmapItem):
    """
    Class representing view of single Card on the gameboard.
    Keywords:
    yo - yours
    op - opponent
    sh - shield
    mn - mana
    hd - hand
    bf - battlefield
    sf - spellfield
    gv - graveyard
    """

    def __init__(self, set, iden, parent=None):
        super(CardView, self).__init__()
        self.set = set
        self.iden = iden
        self.disable_ui = False
        self.parent = parent
        self.card = None

    def mousePressEvent(self, event):
        super(CardView, self).mousePressEvent(event)
        if not self.parent.locked:
            self.parent.locked = True
            self.parent.start_time()
            if self.card is not None:
                self.parent.card_clicked(self.x(), self.y(), self.card.id)
            else:
                self.parent.card_clicked(self.x(), self.y())
            
    def set_card(self, card):
        self.card = card

    def check_if_card_in_target(self):
        for set, targets in self.parent.get_selected_card_targets():
            if set == self.set:
                if len(targets) == 0:
                    continue
                else:
                    if targets[0] == "*":
                        # Allow all cards in that zone to be selected
                        return True
                    return self.iden in targets
        return False

    def contextMenuEvent(self, event):
        your_turn = self.parent.get_your_turn()
        select_mode = self.parent.get_select_mode()
        selected_card = self.parent.get_selected_card()
        if your_turn == 0:
            return
        menu = QMenu()
        if select_mode == 1 and (self.set, self.iden) in selected_card:
            unchoose_action = QAction("Cancel selection")
            unchoose_action.triggered.connect(lambda: self.m_unchoose_card(self.set, self.iden))
            menu.addAction(unchoose_action)
        elif select_mode == 1 and self.check_if_card_in_target():
            choose_action = QAction("Choose a card")
            choose_action.triggered.connect(lambda: self.m_choose_card(self.set, self.iden))
            menu.addAction(choose_action)
        if self.set == 'yu_hd':
            summon_action = QAction("Play a card")
            summon_action.triggered.connect(lambda: self.m_summon_card(self.iden))
            menu.addAction(summon_action)
            mana_action = QAction("Add card to mana")
            mana_action.triggered.connect(lambda: self.m_add_to_mana(self.iden))
            menu.addAction(mana_action)
            shield_action = QAction("Add card to shields")
            shield_action.triggered.connect(lambda: self.m_add_to_shield(self.iden))
            menu.addAction(shield_action)
        elif self.set == 'op_hd':
            peek_action = QAction("Look at card")
            peek_action.triggered.connect(lambda: self.m_opp_look_at_hand(self.iden))
            menu.addAction(peek_action)
            hand_action = QAction('Look at hand')
            hand_action.triggered.connect(lambda: self.m_opp_look_at_hand(-1))
            menu.addAction(hand_action)
        elif self.set == 'yu_sh':
            if self.parent.shields.is_shield_visible(self.iden):
                add_shield_to_hand_action = QAction('Add to hand')
                add_shield_to_hand_action.triggered.connect(lambda: self.m_return_shield_to_hand(self.iden))
                menu.addAction(add_shield_to_hand_action)
                # TODO: if creature and there is no space, hide this option
                for effect in self.parent.shields[self.iden].effects:
                    if "shieldtrigger" in effect:
                        use_effect_from_shield = QAction('Trigger it\'s effect')
                        use_effect_from_shield.triggered.connect(lambda: self.m_play_destroyed_shield(self.set, self.iden))
                        menu.addAction(use_effect_from_shield)
                        break
            # TODO: hide these options
            peek_action = QAction('Look at shield')
            peek_action.triggered.connect(lambda: self.m_look_at_shield(self.iden))
            menu.addAction(peek_action)
            put_action = QAction('Put down a shield')
            put_action.triggered.connect(lambda: self.m_put_shield(self.iden))
            menu.addAction(put_action)
        elif self.set == 'op_sh':
            if self.parent.can_attack_shield() and select_mode in [2, 21]:
                select_action = QAction('Select shield to attack')
                select_action.triggered.connect(lambda: self.m_select_shield_to_attack(self.iden))
                menu.addAction(select_action)
            peek_action = QAction('Look at shield')
            peek_action.triggered.connect(lambda: self.m_opp_look_at_shield(self.iden))
            menu.addAction(peek_action)
        elif self.set == 'yu_mn':
            tap_action = QAction("Tap mana")
            tap_action.triggered.connect(lambda: self.m_tap_mana(self.set, self.iden))
            menu.addAction(tap_action)
            untap_action = QAction('Untap mana')
            untap_action.triggered.connect(lambda: self.m_untap_mana(self.set, self.iden))
            menu.addAction(untap_action)
            return_action = QAction("Return a card to hand")
            return_action.triggered.connect(lambda: self.m_return_card_to_hand(self.set, self.iden))
            menu.addAction(return_action)
            destroy_action = QAction("Move a card to graveyard")
            destroy_action.triggered.connect(lambda: self.m_move_to_graveyard(self.set, self.iden))
            menu.addAction(destroy_action)
        elif self.set == 'op_mn':
            return_action = QAction("Return a card to hand")
            return_action.triggered.connect(lambda: self.m_return_card_to_hand(self.set, self.iden))
            menu.addAction(return_action)
            destroy_action = QAction("Move a card to graveyard")
            destroy_action.triggered.connect(lambda: self.m_move_to_graveyard(self.set, self.iden))
            menu.addAction(destroy_action)
        elif self.set == 'yu_bf':
            if your_turn == 3 and self.iden in self.parent.blocker_list:
                block_action = QAction("Block with this creature")
                block_action.triggered.connect(lambda: self.m_block_with_creature(self.set, self.iden))
                menu.addAction(block_action)
            elif your_turn == 4 and self.iden in self.parent.blocker_list:
                block_action = QAction("Block with this creature")
                block_action.triggered.connect(lambda: self.m_shield_block_with_creature(self.set, self.iden))
                menu.addAction(block_action)
            if not self.parent.bfield.has_summon_sickness(self.iden) and not self.parent.bfield.is_tapped(self.iden):
                can_attack = True
                for effect in self.parent.bfield[self.iden].effects:
                    if "notattacking" in effect:
                        if effect["notattacking"]["mode"] == "all":
                            can_attack = False
                            break
                if can_attack:
                    attack_action = QAction("Attack with this creature")
                    attack_action.triggered.connect(lambda: self.m_select_creature(self.set, self.iden))
                    menu.addAction(attack_action)
            if select_mode == 2 and (self.set, self.iden) in selected_card:
                unselect_action = QAction("Unselect this card")
                unselect_action.triggered.connect(lambda: self.m_unselect_creature(self.set, self.iden))
                menu.addAction(unselect_action)
            return_action = QAction("Return a card to hand")
            return_action.triggered.connect(lambda: self.m_return_card_to_hand(self.set, self.iden))
            menu.addAction(return_action)
            destroy_action = QAction("Move a card to graveyard")
            destroy_action.triggered.connect(lambda: self.m_move_to_graveyard(self.set, self.iden))
            menu.addAction(destroy_action)
        elif self.set == 'op_bf':
            if select_mode == 2:
                if self.parent.opp_bfield.is_tapped(self.iden):
                    select_action = QAction("Target card to attack")
                    select_action.triggered.connect(lambda: self.m_attack_creature(self.set, self.iden))
                    menu.addAction(select_action)
                else:
                    # check if selected creature can attack untapped creatures
                    for effect in self.parent.bfield[selected_card[0][1]].effects:
                        if "canattackuntapped" in effect.keys():
                            select_action = QAction("Target card to attack")
                            select_action.triggered.connect(lambda: self.m_attack_creature(self.set, self.iden))
                            menu.addAction(select_action)
            # TODO: hide these options
            return_action = QAction("Return a card to hand")
            return_action.triggered.connect(lambda: self.m_return_card_to_hand(self.set, self.iden))
            menu.addAction(return_action)
            destroy_action = QAction("Move a card to graveyard")
            destroy_action.triggered.connect(lambda: self.m_move_to_graveyard(self.set, self.iden))
            menu.addAction(destroy_action)
        elif self.set == 'op_gv':
            look_action = QAction('Look at opponent graveyard')
            look_action.triggered.connect(lambda: self.m_look_graveyard(self.set))
            menu.addAction(look_action)
        elif self.set == 'yu_gv':
            look_action = QAction('Look at your graveyard')
            look_action.triggered.connect(lambda: self.m_look_graveyard(self.set))
            menu.addAction(look_action)
        menu.exec_(QCursor.pos())
        
    def m_summon_card(self, iden):
        self.parent.a_summon_card(iden)

    def m_choose_card(self, set, iden):
        self.parent.a_choose_card(set, iden)

    def m_unchoose_card(self, set, iden):
        self.parent.a_unchoose_card(set, iden)
        
    def m_return_card_to_hand(self, set, iden):
        self.parent.a_return_card_to_hand(set, iden)
        
    def m_return_shield_to_hand(self, iden):
        self.parent.a_return_shield_to_hand(iden)

    def m_play_destroyed_shield(self, set, iden):
        self.parent.a_play_destroyed_shield(set, iden)

    def m_move_to_graveyard(self, set, iden):
        self.parent.a_move_to_graveyard(set, iden)
        
    def m_add_to_mana(self, iden):
        self.parent.a_add_to_mana(iden)
        
    def m_add_to_shield(self, iden):
        self.parent.a_add_to_shield(iden)
        
    def m_tap_mana(self, set, iden):
        self.parent.a_tap_mana(set, iden)
        
    def m_untap_mana(self, set, iden):
        self.parent.a_untap_mana(set, iden)
        
    def m_look_at_shield(self, iden):
        self.parent.a_look_at_shield(iden)

    def m_put_shield(self, iden):
        self.parent.a_put_shield(iden)
        
    def m_select_creature(self, set, iden):
        self.parent.a_select_creature(set, iden)

    def m_unselect_creature(self, set, iden):
        self.parent.a_unselect_creature(set, iden)

    def m_attack_creature(self, set, iden):
        self.parent.a_attack_creature(set, iden)

    def m_select_shield_to_attack(self, iden):
        self.parent.a_select_shield_to_attack(iden)

    def m_remove_shield_to_attack(self, iden):
        self.parent.a_remove_shield_to_attack(iden)

    def m_block_with_creature(self, set, iden):
        self.parent.a_block_with_creature(set, iden)

    def m_shield_block_with_creature(self, set, iden):
        self.parent.a_shield_block_with_creature(set, iden)
   
    def m_opp_look_at_hand(self, iden):
        self.parent.a_opp_look_at_hand(iden)
        
    def m_opp_look_at_shield(self, iden):
        self.parent.a_opp_look_at_shield(iden)
        
    def m_look_graveyard(self, set):
        self.parent.a_look_graveyard(set)
