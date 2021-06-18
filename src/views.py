from PySide2.QtCore import QObject, Slot
from PySide2.QtGui import QCursor, QTransform
from PySide2.QtWidgets import QGraphicsScene, QGraphicsPixmapItem, QMenu, QAction, QWidget

from src.ui.ui_graveyard import Ui_Graveyard


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
            if self.parent.your_turn == 0:
                return
            menu = QMenu()
            print(f"BOARD: SELECT MODE - {str(self.parent.select_mode)}, {len(self.parent.selected_card)} == {self.parent.card_to_choose}")
            if self.parent.select_mode == 1 and len(self.parent.selected_card) == self.parent.card_to_choose:
                accept_action = QAction("Trigger effect")
                accept_action.triggered.connect(self.parent.m_accept_cards)
                menu.addAction(accept_action)
            if self.parent.debug_mode:
                draw_action = QAction("Draw a card")
                draw_action.triggered.connect(self.parent.m_draw_a_card)
                menu.addAction(draw_action)
            end_action = QAction("End turn")
            end_action.triggered.connect(self.parent.m_end_turn)
            menu.addAction(end_action)
            menu.exec_(QCursor.pos())


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
        if self.parent.your_turn == 0:
            return
        menu = QMenu()
        if self.parent.select_mode == 1 and (self.set, self.iden) in self.parent.selected_card:
            unchoose_action = QAction("Cancel selection")
            unchoose_action.triggered.connect(lambda: self.parent.m_unchoose_card(self.set, self.iden))
            menu.addAction(unchoose_action)
        elif self.parent.select_mode == 1 and self.set in self.parent.type_to_choose:
            choose_action = QAction("Choose a card")
            choose_action.triggered.connect(lambda: self.parent.m_choose_card(self.set, self.iden))
            menu.addAction(choose_action)
        if self.set == 'yu_hd':
            summon_action = QAction("Play a card")
            summon_action.triggered.connect(lambda: self.parent.m_summon_card(self.iden))
            menu.addAction(summon_action)
            mana_action = QAction("Add card to mana")
            mana_action.triggered.connect(lambda: self.parent.m_add_to_mana(self.iden))
            menu.addAction(mana_action)
            shield_action = QAction("Add card to shields")
            shield_action.triggered.connect(lambda: self.parent.m_add_to_shield(self.iden))
            menu.addAction(shield_action)
        elif self.set == 'op_hd':
            peek_action = QAction("Look at card")
            peek_action.triggered.connect(lambda: self.parent.m_opp_look_at_hand(self.iden))
            menu.addAction(peek_action)
            hand_action = QAction('Look at hand')
            hand_action.triggered.connect(lambda: self.parent.m_opp_look_at_hand(-1))
            menu.addAction(hand_action)
        elif self.set == 'yu_sh':
            # TODO: if shield was destroyed, it's your time to decide what to do with it
            print(f"SHIELD DESTOYED: POS {self.iden}")
            if self.parent.shields.is_shield_visible(self.iden - 1):
                add_shield_to_hand_action = QAction('Add to hand')
                add_shield_to_hand_action.triggered.connect(lambda: self.parent.m_return_shield_to_hand(self.iden))
                menu.addAction(add_shield_to_hand_action)
                # TODO: if creature and there is no space, hide this option
                if "shieldtrigger" in self.parent.database.get_card(self.shields[self.iden - 1][0]).effects:
                    use_effect_from_shield = QAction('Trigger it\'s effect')
                    use_effect_from_shield.triggered.connect(lambda: self.parent.m_play_destroyed_shield(self.set, self.iden))
                    menu.addAction(use_effect_from_shield)
            peek_action = QAction('Look at shield')
            peek_action.triggered.connect(lambda: self.parent.m_look_at_shield(self.iden))
            menu.addAction(peek_action)
            put_action = QAction('Put down a shield')
            put_action.triggered.connect(lambda: self.parent.m_put_shield(self.iden))
            menu.addAction(put_action)
        elif self.set == 'op_sh':
            # TODO: check if selected card can attack shields
            if self.parent.can_attack_shield() and True: # TODO: only on specific mode
                select_action = QAction('Select shield to attack')
                select_action.triggered.connect(lambda: self.parent.m_shield_attack(self.iden))
                menu.addAction(select_action)
            peek_action = QAction('Look at shield')
            peek_action.triggered.connect(lambda: self.parent.m_opp_look_at_shield(self.iden))
            menu.addAction(peek_action)
        elif self.set == 'yu_mn':
            tap_action = QAction("Tap mana")
            tap_action.triggered.connect(lambda: self.parent.m_tap_mana(self.set, self.iden))
            menu.addAction(tap_action)
            untap_action = QAction('Untap mana')
            untap_action.triggered.connect(lambda: self.parent.m_untap_mana(self.set, self.iden))
            menu.addAction(untap_action)
            return_action = QAction("Return a card to hand")
            return_action.triggered.connect(lambda: self.parent.m_return_card_to_hand(self.set, self.iden))
            menu.addAction(return_action)
            destroy_action = QAction("Move a card to graveyard")
            destroy_action.triggered.connect(lambda: self.parent.m_move_to_graveyard(self.set, self.iden))
            menu.addAction(destroy_action)
        elif self.set == 'op_mn':
            return_action = QAction("Return a card to hand")
            return_action.triggered.connect(lambda: self.parent.m_return_card_to_hand(self.set, self.iden))
            menu.addAction(return_action)
            destroy_action = QAction("Move a card to graveyard")
            destroy_action.triggered.connect(lambda: self.parent.m_move_to_graveyard(self.set, self.iden))
            menu.addAction(destroy_action)
        elif self.set == 'yu_bf':
            attack_action = QAction("Attack with this creature")
            attack_action.triggered.connect(lambda: self.parent.m_select_creature(self.set, self.iden))
            menu.addAction(attack_action)
            if self.parent.select_mode == 2 and (self.set, self.iden) in self.parent.selected_card:
                unselect_action = QAction("Unselect this card")
                unselect_action.triggered.connect(lambda: self.parent.m_unselect_creature(self.set, self.iden))
                menu.addAction(unselect_action)
            return_action = QAction("Return a card to hand")
            return_action.triggered.connect(lambda: self.parent.m_return_card_to_hand(self.set, self.iden))
            menu.addAction(return_action)
            destroy_action = QAction("Move a card to graveyard")
            destroy_action.triggered.connect(lambda: self.parent.m_move_to_graveyard(self.set, self.iden))
            menu.addAction(destroy_action)
        elif self.set == 'op_bf':
            select_action = QAction("Target card to attack/cast")
            select_action.triggered.connect(lambda: self.parent.m_attack_creature(self.set, self.iden))
            menu.addAction(select_action)
            return_action = QAction("Return a card to hand")
            return_action.triggered.connect(lambda: self.parent.m_return_card_to_hand(self.set, self.iden))
            menu.addAction(return_action)
            destroy_action = QAction("Move a card to graveyard")
            destroy_action.triggered.connect(lambda: self.parent.m_move_to_graveyard(self.set, self.iden))
            menu.addAction(destroy_action)
        elif self.set == 'op_gv':
            look_action = QAction('Look at opponent graveyard')
            look_action.triggered.connect(lambda: self.parent.m_look_graveyard(self.set))
            menu.addAction(look_action)
        elif self.set == 'yu_gv':
            look_action = QAction('Look at your graveyard')
            look_action.triggered.connect(lambda: self.parent.m_look_graveyard(self.set))
            menu.addAction(look_action)
        menu.exec_(QCursor.pos())

            
class GraveyardView(QWidget):
    """
    """
    def __init__(self, graveyard, parent=None):
        super(GraveyardView, self).__init__()
        self.ui = Ui_Graveyard()
        self.ui.setupUi(self)
        self.graveyard = graveyard
        self.parent = parent
        self.ui.closeButton.clicked.connect(self.close)
        self.draw_graveyard()

    def draw_graveyard(self):
        print(len(self.graveyard))

        
