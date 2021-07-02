from src.ui.ui_graveyard import Ui_Graveyard

from PySide2.QtCore import QObject, Slot, Qt
from PySide2.QtGui import QCursor, QTransform, QPixmap
from PySide2.QtWidgets import QGraphicsScene, QGraphicsPixmapItem, QMenu, QAction, QWidget

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
        self.ui.graphicsView.setScene(self.graveyardScene) # TODO: replace QGraphicView with custom view to support scrolling

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
                    card = self.graveyard[offset+ind]
                    self.draw_card(x, y, card)
                    x += 90
                    ind += 1
            x = 5
            y += 120

    def draw_card(self, x, y, card):
        """
        Draw card item with its image on the screen
        """
        item = GraveyardCardHandle(card.id, self)
        pixmap = QPixmap()
        if not pixmap.loadFromData(self.parent.database.get_data(card.id, 'low_res')):
            pass
        item.setPixmap(pixmap)
        item.setPos(x, y)
        self.graveyardScene.addItem(item)
        # TODO: draw outline if selected

class GraveyardCardHandle(QGraphicsPixmapItem):
    """
    Single card handle to check more info, add or remove card from your deck.
    """
    def __init__(self, set, iden, parent):
        super(GraveyardCardHandle, self).__init__()
        self.parent = parent
        self.set = set
        self.iden = iden

    def contextMenuEvent(self, event):
        your_turn = self.parent.get_your_turn()
        select_mode = self.parent.get_select_mode()
        selected_card = self.parent.get_selected_card()
        if your_turn == 0:
            return
        menu = QMenu()
        select_action = QAction('Select card from the graveyard')
        select_action.triggered.connect(lambda: self.m_select_card(self.set, self.iden))
        menu.addAction(select_action)
        unselect_action = QAction('Unselect card')
        unselect_action.triggered.connect(lambda: self.m_select_card(self.set, self.iden))
        menu.addAction(unselect_action)
        menu.exec_(QCursor.pos())

    def m_select_card(self, set, iden):
        pass

    def m_unselect_card(self, set, iden):
        pass

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