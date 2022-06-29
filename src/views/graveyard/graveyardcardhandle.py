from PySide6.QtCore import QObject, Slot, Qt
from PySide6.QtGui import QCursor, QTransform, QPixmap, QAction
from PySide6.QtWidgets import QGraphicsScene, QGraphicsPixmapItem, QMenu, QWidget, QGraphicsView


class GraveyardCardHandle(QGraphicsPixmapItem):
    """
    Single card handle to check more info, add or remove card from your deck.
    """
    def __init__(self, iden, parent):
        super(GraveyardCardHandle, self).__init__()
        self.parent = parent
        self.iden = iden

    def contextMenuEvent(self, event):
        your_turn = self.parent.get_your_turn()
        select_mode = self.parent.get_select_mode()
        selected_card = self.parent.get_selected_card()
        if your_turn == 0:
            return
        menu = QMenu()
        select_action = QAction('Select card from the graveyard')
        select_action.triggered.connect(lambda: self.m_select_card(self.iden))
        menu.addAction(select_action)
        unselect_action = QAction('Unselect card')
        unselect_action.triggered.connect(lambda: self.m_select_card(self.iden))
        menu.addAction(unselect_action)
        menu.exec_(QCursor.pos())

    def m_select_card(self, iden):
        pass

    def m_unselect_card(self, iden):
        pass

    # def mousePressEvent(self, event):
    #     if event.button() == Qt.MiddleButton:
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