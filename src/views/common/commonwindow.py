from src.ui.ui_common import Ui_CommonDialog

from PySide6.QtCore import QObject, Slot, Qt, Signal
from PySide6.QtGui import QCursor, QTransform, QPixmap, QAction, QColor, QPen
from PySide6.QtWidgets import QGraphicsScene, QGraphicsPixmapItem, QMenu, QWidget, QGraphicsView

from src.views.common.commoncardhandle import CommonCardHandle


class CommonWindow(QWidget):
    """
    View to check on graveyard cards
    TODO: center scene in view
    TODO: implement card selecting in case of effects
    """
    card_choosed = Signal()
    def __init__(self, settings, parent):
        super(CommonWindow, self).__init__()
        self.ui = Ui_CommonDialog()
        self.ui.setupUi(self)
        self.ui.selectButton.clicked.connect(self.return_selected_items)

        self.cards = settings["cards"]
        self.type = settings["type"]
        self.count = settings["count"]

        self.parent = parent

        self.scene = QGraphicsScene(self)
        self.ui.graphicsView.setScene(self.scene)

        self.row_size = 3
        self.column_size = 4

        self.actual_row = 0

        self._selected_cards = [] # positions of the cards in self.cards

        self.redraw()

    def redraw(self):
        """
        Redraw all the elements on the GraphicsScene
        """
        offset = self.actual_row * self.row_size
        x = 5
        y = 5
        ind = 0
        self.scene.clear()
        for _ in range(self.column_size):
            for _ in range(self.row_size):
                if ind+offset < len(self.cards):
                    self.draw_card(x, y, ind+offset)
                    x += 90
                    ind += 1
            x = 5
            y += 120

    def draw_card(self, x, y, card_pos):
        """
        Draw card item with its image on the screen
        """
        card_id = self.cards[card_pos]
        item = CommonCardHandle(card_pos, self)
        pixmap = QPixmap()
        if not pixmap.loadFromData(self.parent.database.get_data(card_id, 'low_res')):
            # TODO: throw error or something
            pass
        item.setPixmap(pixmap)
        item.setPos(x, y)
        self.scene.addItem(item)

        if card_pos in self.get_selected_cards():
            self.draw_highlight(x, x + 85, y, y + 115, QColor(255, 0, 0))

    def draw_highlight(self, x1, x2, y1, y2, color):
        """
        Draw a frame around a clicked card on the board
        """
        self.scene.addLine(x1 - 1, y1 - 1, x1 - 1, y2 + 1, QPen(color))
        self.scene.addLine(x2 + 1, y1 - 1, x2 + 1, y2 + 1, QPen(color))
        self.scene.addLine(x1 - 1, y1 - 1, x2 + 1, y1 - 1, QPen(color))
        self.scene.addLine(x1 - 1, y2 + 1, x2 + 1, y2 + 1, QPen(color))

    def add_selected_cards(self, iden):
        self._selected_cards.append(iden)
        self.redraw()

    def remove_selected_cards(self, iden):
        self._selected_cards.remove(iden)
        self.redraw()

    def get_selected_cards(self):
        # Get selected cards by position
        return self._selected_cards

    def get_selected_items(self):
        # Get selected cards by id
        return [self.cards[pos] for pos in self.get_selected_cards()]

    @Slot()
    def return_selected_items(self):
        # TODO: validate if can be closed
        self.card_choosed.emit()
        self.close()
