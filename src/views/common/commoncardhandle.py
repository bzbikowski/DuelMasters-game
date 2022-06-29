from PySide6.QtCore import QObject, Slot, Qt
from PySide6.QtGui import QCursor, QTransform, QPixmap, QAction
from PySide6.QtWidgets import QGraphicsScene, QGraphicsPixmapItem, QMenu, QWidget, QGraphicsView


class CommonCardHandle(QGraphicsPixmapItem):
    """
    Single card handle to check more info, add or remove card from your deck.
    """
    def __init__(self, cards_pos, parent):
        super(CommonCardHandle, self).__init__()
        self.parent = parent
        self.cards_pos = cards_pos

    def contextMenuEvent(self, event):
        selected_cards = self.parent.get_selected_cards()
        menu = QMenu()
        if self.cards_pos in selected_cards:
            unselect_action = QAction('Unselect card')
            unselect_action.triggered.connect(lambda: self.m_select_card(self.cards_pos))
            menu.addAction(unselect_action)
        else:
            if len(selected_cards) < self.parent.count:
                select_action = QAction('Select card')
                select_action.triggered.connect(lambda: self.m_select_card(self.cards_pos))
                menu.addAction(select_action)
        menu.exec_(QCursor.pos())

    def m_select_card(self, cards_pos):
        self.parent.add_selected_cards(cards_pos)

    def m_unselect_card(self, cards_pos):
        self.parent.remove_selected_cards(cards_pos)

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