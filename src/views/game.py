from PySide6.QtCore import QObject, Slot, Qt
from PySide6.QtGui import QCursor, QTransform, QPixmap, QAction
from PySide6.QtWidgets import QGraphicsScene, QGraphicsPixmapItem, QMenu, QWidget


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
                if select_mode == 1 and len(self.parent.get_selected_card()) == self.parent.get_selected_card_choose():
                    accept_action = QAction("Trigger effect")
                    accept_action.triggered.connect(self.m_accept_cards)
                    menu.addAction(accept_action)
                if select_mode == 21 and self.parent.bfield.get_shield_count(self.parent.get_selected_card()[0][1]) == len(self.parent.get_selected_shields()): # TODO: test it
                    shield_action = QAction("Confirm shields attack")
                    shield_action.triggered.connect(self.m_shield_attack)
                    menu.addAction(shield_action)
                if select_mode == 2 and self.parent.opp_shields.get_count() == 0: # TODO: check if card can attack players
                    direct_action = QAction("Attack player directly")
                    direct_action.triggered.connect(self.m_direct_attack)
                    menu.addAction(direct_action)
                if your_turn == 3:
                    pass_action = QAction("Do not block the attack")
                    pass_action.triggered.connect(self.m_pass_attack)
                    menu.addAction(pass_action)
                elif your_turn == 4:
                    pass_action = QAction("Do not block the attack")
                    pass_action.triggered.connect(self.m_shield_pass_attack)
                    menu.addAction(pass_action)
                elif your_turn == 5:
                    pass_action = QAction("Do not block the attack")
                    pass_action.triggered.connect(self.m_direct_pass_attack)
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
        self.parent.a_draw_card()

    def m_end_turn(self):
        # Action: end your turn
        self.parent.a_end_turn()

    def m_shield_attack(self):
        self.parent.a_shield_attack()

    def m_direct_attack(self):
        self.parent.a_direct_attack()

    def m_pass_attack(self):
        self.parent.a_pass_attack()

    def m_shield_pass_attack(self): 
        self.parent.a_shield_pass_attack()

    def m_direct_pass_attack(self):
        self.parent.lose()

    def m_debug_info(self):
        self.parent.a_debug_info()
