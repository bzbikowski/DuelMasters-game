from PySide2.QtCore import QObject, Slot, Qt
from PySide2.QtGui import QCursor, QTransform, QPixmap
from PySide2.QtWidgets import QGraphicsScene, QGraphicsPixmapItem, QMenu, QAction, QWidget


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