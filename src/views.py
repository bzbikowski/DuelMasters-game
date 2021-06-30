from PySide2.QtCore import QObject, Slot, Qt
from PySide2.QtGui import QCursor, QTransform, QPixmap
from PySide2.QtWidgets import QGraphicsScene, QGraphicsPixmapItem, QMenu, QAction, QWidget

from src.ui.ui_graveyard import Ui_Graveyard
from src.ui.ui_deck import Ui_Deck


class GameView(QGraphicsScene):
    """
    Main scene in Game class, which displays GUI and cards currently on gameboard.
    This class is extended to support mouse buttons.
    Right mouse button creates context menu to choose actions about the game.
    """
    def __init__(self, parent=None):
        # todo something is breaking when clicked on card
        super(GameView, self).__init__(parent)
        self.disable_ui = False
        self.parent = parent

    def mousePressEvent(self, event):
        if self.parent.focus_request:
            self.parent.focus_request = False
            self.parent.refresh_screen()
        super(GameView, self).mousePressEvent(event)

    def contextMenuEvent(self, event):
        point = self.itemAt(event.scenePos(), QTransform())
        if point is not self.parent.background:
            point.contextMenuEvent(event)
        else:
            your_turn = self.parent.get_your_turn()
            select_mode = self.parent.get_select_mode()
            if your_turn == 0: # TODO: remove later
                menu = QMenu()
                debug_action = QAction("Print debug info")
                debug_action.triggered.connect(self.m_debug_info)
                menu.addAction(debug_action)
                menu.exec_(QCursor.pos())
            else:
                menu = QMenu()
                if select_mode == 1 and len(self.parent.get_selected_card()) == self.parent.get_card_to_choose():
                    accept_action = QAction("Trigger effect")
                    accept_action.triggered.connect(self.m_accept_cards)
                    menu.addAction(accept_action)
                if select_mode == 21 and True: # TODO: check if number of shield selected matches shieldbreaker ability
                    shield_action = QAction("Confirm shields attack")
                    shield_action.triggered.connect(self.m_shield_attack)
                    menu.addAction(shield_action)
                if your_turn == 3:
                    pass_action = QAction("Do not block the attack")
                    pass_action.triggered.connect(self.m_pass_attack)
                    menu.addAction(pass_action)
                elif your_turn == 4:
                    pass_action = QAction("Do not block the attack")
                    pass_action.triggered.connect(self.m_shield_pass_attack)
                    menu.addAction(pass_action)
                end_action = QAction("End turn")
                end_action.triggered.connect(self.m_end_turn)
                menu.addAction(end_action)
                debug_action = QAction("Print debug info")
                debug_action.triggered.connect(self.m_debug_info)
                menu.addAction(debug_action)
                menu.exec_(QCursor.pos())

    def m_accept_cards(self):
        action, args = self.parent.pop_fun_queue(0)
        action(*args)

    def m_draw_a_card(self):
        self.parent.draw_card()

    def m_end_turn(self):
        # Action: end your turn
        self.parent.end_turn()

    def m_shield_attack(self):
        self.parent.shield_attack()

    def m_pass_attack(self):
        self.parent.pass_attack()

    def m_shield_pass_attack(self): 
        self.parent.shield_pass_attack()

    def m_debug_info(self):
        print("====DEBUG====")
        print(f"your_turn: {self.parent.get_your_turn()}")
        print(f"select_mode: {self.parent.get_select_mode()}")
        print(f"selected_card: {self.parent.get_selected_card()}")
        print(f"selected_shields: {self.parent.get_selected_shields()}")
        print("=============")


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
        elif select_mode == 1 and self.set in self.parent.get_type_to_choose():
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
            peek_action = QAction('Look at shield')
            peek_action.triggered.connect(lambda: self.m_look_at_shield(self.iden))
            menu.addAction(peek_action)
            put_action = QAction('Put down a shield')
            put_action.triggered.connect(lambda: self.m_put_shield(self.iden))
            menu.addAction(put_action)
        elif self.set == 'op_sh':
            # TODO: check if selected card can attack shields
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
        self.parent.summon_card(iden)

    def m_choose_card(self, set, iden):
        self.parent.choose_card(set, iden)

    def m_unchoose_card(self, set, iden):
        self.parent.unchoose_card(set, iden)
        
    def m_return_card_to_hand(self, set, iden):
        self.parent.return_card_to_hand(set, iden)
        
    def m_return_shield_to_hand(self, iden):
        self.parent.return_shield_to_hand(iden)

    def m_play_destroyed_shield(self, set, iden):
        self.parent.play_destroyed_shield(set, iden)

    def m_move_to_graveyard(self, set, iden):
        self.parent.move_to_graveyard(set, iden)
        
    def m_add_to_mana(self, iden):
        self.parent.add_to_mana(iden)
        
    def m_add_to_shield(self, iden):
        self.parent.add_to_shield(iden)
        
    def m_tap_mana(self, set, iden):
        self.parent.tap_mana(set, iden)
        
    def m_untap_mana(self, set, iden):
        self.parent.untap_mana(set, iden)
        
    def m_look_at_shield(self, iden):
        self.parent.look_at_shield(iden)

    def m_put_shield(self, iden):
        self.parent.put_shield(iden)
        
    def m_select_creature(self, set, iden):
        self.parent.select_creature(set, iden)

    def m_unselect_creature(self, set, iden):
        self.parent.unselect_creature(set, iden)

    def m_attack_creature(self, set, iden):
        self.parent.attack_creature(set, iden)

    def m_select_shield_to_attack(self, iden):
        self.parent.select_shield_to_attack(iden)

    def m_remove_shield_to_attack(self, iden):
        self.parent.remove_shield_to_attack(iden)

    def m_block_with_creature(self, set, iden):
        self.parent.block_with_creature(set, iden)

    def m_shield_block_with_creature(self, set, iden):
        self.parent.shield_block_with_creature(set, iden)
   
    def m_opp_look_at_hand(self, iden):
        self.parent.opp_look_at_hand(iden)
        
    def m_opp_look_at_shield(self, iden):
        self.parent.opp_look_at_shield(iden)
        
    def m_look_graveyard(self, set):
        self.parent.look_graveyard(set)


class GraveyardView(QWidget):
    """
    View to check on graveyard cards
    TODO: center scene in view
    TODO: implement card selecting in case of effects
    """
    def __init__(self, graveyard, parent=None):
        super(GraveyardView, self).__init__()
        self.ui = Ui_Graveyard()
        self.ui.setupUi(self)
        self.ui.closeButton.clicked.connect(self.close)

        self.graveyard = graveyard
        self.parent = parent

        self.graveyardScene = QGraphicsScene(self)
        self.ui.graphicsView.setScene(self.graveyardScene)

        self.row_size = 3
        self.column_size = 4

        self.actual_row = 0

        self.redraw()

    def redraw(self):
        """
        Redraw all the elements on the GraphicsScene
        """
        offset = self.actual_row * self.row_size
        x = 5
        y = 5
        ind = 0
        for _ in range(self.column_size):
            for _ in range(self.row_size):
                if ind+offset < len(self.graveyard):
                    id = self.graveyard[offset+ind].id
                    self.draw_card(x, y, id)
                    x += 90
                    ind += 1
            x = 5
            y += 120

    def draw_card(self, x, y, id):
        """
        Draw card item with its image on the screen
        """
        card = CardHandle(id, self)
        pixmap = QPixmap()
        if not pixmap.loadFromData(self.parent.database.get_data(id, 'low_res')):
            pass
        card.setPixmap(pixmap)
        card.setPos(x, y)
        self.graveyardScene.addItem(card)

class CardHandle(QGraphicsPixmapItem):
    """
    Single card handle to check more info, add or remove card from your deck.
    """
    def __init__(self, id, parent):
        super(CardHandle, self).__init__()
        self.parent = parent
        self.id = id

    # def mousePressEvent(self, event):
    #     if event.button() == Qt.MidButton:
    #         self.parent.pop_window(self.id)
    #         return
    #     if event.button() == Qt.LeftButton:
    #         if len(self.parent.deck) < 40:
    #             if self.parent.deck.count(self.id) < 4:
    #                 self.parent.deck.append(self.id)
    #     elif event.button() == Qt.RightButton:
    #         if self.id in self.parent.deck:
    #             index = self.parent.deck.index(self.id)
    #             self.parent.deck.pop(index)
    #     self.parent.redraw()

class DeckView(QWidget):
    """
    View to check on deck cards
    TODO: center scene in view
    TODO: implement card selecting in case of effects
    """
    def __init__(self, deck, parent=None):
        super(DeckView, self).__init__()
        self.ui = Ui_Deck()
        self.ui.setupUi(self)
        self.ui.closeButton.clicked.connect(self.close)

        self.deck = deck
        self.parent = parent

        self.deckScene = QGraphicsScene(self)
        self.ui.graphicsView.setScene(self.deckScene)

        self.row_size = 3
        self.column_size = 4

        self.actual_row = 0

        self.redraw()

    def redraw(self):
        """
        Redraw all the elements on the GraphicsScene
        """
        offset = self.actual_row * self.row_size
        x = 5
        y = 5
        ind = 0
        for _ in range(self.column_size):
            for _ in range(self.row_size):
                if ind+offset < len(self.graveyard):
                    id = self.graveyard[offset+ind].id
                    self.draw_card(x, y, id)
                    x += 90
                    ind += 1
            x = 5
            y += 120

    def draw_card(self, x, y, id):
        """
        Draw card item with its image on the screen
        """
        card = CardHandle(id, self)
        pixmap = QPixmap()
        if not pixmap.loadFromData(self.parent.database.get_data(id, 'low_res')):
            pass
        card.setPixmap(pixmap)
        card.setPos(x, y)
        self.graveyardScene.addItem(card)