from PyQt5.QtWidgets import QGraphicsScene, QGraphicsPixmapItem, QMenu, QAction, QWidget
from PyQt5.QtGui import QCursor, QTransform


class GameView(QGraphicsScene):
    """
    Main scene in Game class, which displays GUI and cards currently on gameboard.
    This class is extended to support mouse buttons.
    Right mouse button creates context menu to choose actions about the game.
    """
    def __init__(self, parent=None):
        super(GameView, self).__init__(parent)
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
            menu = QMenu()
            if self.parent.select_mode and len(self.parent.selected_card) == self.parent.card_to_choose:
                end_action = QAction("Accept cards")
                end_action.triggered.connect(self.parent.m_accept_cards)
                menu.addAction(end_action)
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
    gv - graveyard
    """

    def __init__(self, set, iden, parent=None):
        super(CardView, self).__init__()
        self.set = set
        self.iden = iden
        self.parent = parent
        self.card = None

    def mousePressEvent(self, event):
        super(CardView, self).mousePressEvent(event)
        if not self.parent.locked:
            self.parent.locked = True
            self.parent.startTime()
            if self.card is not None:
                self.parent.card_clicked(self.x(), self.y(), self.card.id)
            else:
                self.parent.card_clicked(self.x(), self.y())
            
    def set_card(self, card):
        self.card = card

    def contextMenuEvent(self, event):
        menu = QMenu()
        if self.parent.select_mode and self.set in self.parent.type_to_choose:
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
            peek_action = QAction('Look at shield')
            peek_action.triggered.connect(lambda: self.parent.m_look_at_shield(self.iden))
            menu.addAction(peek_action)
            put_action = QAction('Put down a shield')
            put_action.triggered.connect(lambda: self.parent.m_put_shield(self.iden))
            menu.addAction(put_action)
        elif self.set == 'op_sh':
            peek_action = QAction('Look at shield')
            peek_action.triggered.connect(lambda: self.parent.m_opp_look_at_shield(self.iden))
            menu.addAction(peek_action)
            select_action = QAction('Select shield to attack')
            select_action.triggered.connect(lambda: self.parent.m_opp_shield_attack(self.iden))
            menu.addAction(select_action)
        elif self.set == 'yu_mn':
            tap_action = QAction("Tap mana")
            tap_action.triggered.connect(lambda: self.parent.m_tap_card(self.set, self.iden))
            menu.addAction(tap_action)
            untap_action = QAction('Untap mana')
            untap_action.triggered.connect(lambda: self.parent.m_untap_card(self.set, self.iden))
            menu.addAction(untap_action)
            return_action = QAction("Return a card to hand")
            return_action.triggered.connect(lambda: self.parent.m_return_card_to_hand(self.set, self.iden))
            menu.addAction(return_action)
            destroy_action = QAction("Move a card to graveyard")
            destroy_action.triggered.connect(lambda: self.parent.m_move_to_graveyard(self.set, self.iden))
            menu.addAction(destroy_action)
        elif self.set == 'op_mn':
            return_action = QAction("Return a card to hand")
            return_action.triggered.connect(lambda: self.parent.m_opp_return_card_to_hand(self.set, self.iden))
            menu.addAction(return_action)
            destroy_action = QAction("Move a card to graveyard")
            destroy_action.triggered.connect(lambda: self.parent.m_opp_move_to_graveyard(self.set, self.iden))
            menu.addAction(destroy_action)
        elif self.set == 'yu_bf':
            attack_action = QAction("Attack")
            attack_action.triggered.connect(lambda: self.parent.m_attack_with_creature(self.iden))
            menu.addAction(attack_action)
            target_action = QAction("Target this card")
            menu.addAction(target_action)
            return_action = QAction("Return a card to hand")
            return_action.triggered.connect(lambda: self.parent.m_return_card_to_hand(self.set, self.iden))
            menu.addAction(return_action)
            destroy_action = QAction("Move a card to graveyard")
            destroy_action.triggered.connect(lambda: self.parent.m_move_to_graveyard(self.set, self.iden))
            menu.addAction(destroy_action)
        elif self.set == 'op_bf':
            select_action = QAction("Target card to attack/cast")
            select_action.triggered.connect(lambda: self.parent.m_attack_opp_creature(self.iden))
            menu.addAction(select_action)
            return_action = QAction("Return a card to hand")
            return_action.triggered.connect(lambda: self.parent.m_opp_return_card_to_hand(self.set, self.iden))
            menu.addAction(return_action)
            destroy_action = QAction("Move a card to graveyard")
            destroy_action.triggered.connect(lambda: self.parent.m_opp_move_to_graveyard(self.set, self.iden))
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
    Unfinished graveyard
    """
    def __init__(self, cards, parent=None):
        super(GraveyardView, self).__init__()
        self.width = 800
        self.height = 600
        self.setFixedSize(self.width, self.height)
        print(len(cards))
        
        