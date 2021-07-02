from src.ui.ui_deck import Ui_Deck

from PySide2.QtCore import QObject, Slot, Qt
from PySide2.QtGui import QCursor, QTransform, QPixmap
from PySide2.QtWidgets import QGraphicsScene, QGraphicsPixmapItem, QMenu, QAction, QWidget


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
        card = DeckCardHandle(id, self)
        pixmap = QPixmap()
        if not pixmap.loadFromData(self.parent.database.get_data(id, 'low_res')):
            pass
        card.setPixmap(pixmap)
        card.setPos(x, y)
        self.graveyardScene.addItem(card)


class DeckCardHandle(QGraphicsPixmapItem):
    """
    Single card handle to check more info, add or remove card from your deck.
    """
    def __init__(self, id, parent):
        super(DeckCardHandle, self).__init__()
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