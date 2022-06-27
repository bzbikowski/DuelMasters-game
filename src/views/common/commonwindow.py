from src.ui.ui_common import Ui_CommonDialog

from PySide6.QtCore import QObject, Slot, Qt
from PySide6.QtGui import QCursor, QTransform, QPixmap, QAction
from PySide6.QtWidgets import QGraphicsScene, QGraphicsPixmapItem, QMenu, QWidget, QGraphicsView

from src.views.common.commoncardhandle import CommonCardHandle


class CommonWindow(QWidget):
    """
    View to check on graveyard cards
    TODO: center scene in view
    TODO: implement card selecting in case of effects
    """
    def __init__(self, settings, parent=None):
        super(CommonWindow, self).__init__()
        self.ui = Ui_CommonDialog()
        self.ui.setupUi(self)
        self.ui.closeButton.clicked.connect(self.close)

        self.cards = settings["cards"]
        self.parent = parent

        self.scene = QGraphicsScene(self)
        self.ui.graphicsView.setScene(self.scene)

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
                if ind+offset < len(self.cards):
                    card = self.cards[offset+ind]
                    self.draw_card(x, y, card)
                    x += 90
                    ind += 1
            x = 5
            y += 120

    def draw_card(self, x, y, card):
        """
        Draw card item with its image on the screen
        """
        item = CommonCardHandle(card.id, self)
        pixmap = QPixmap()
        if not pixmap.loadFromData(self.parent.database.get_data(card.id, 'low_res')):
            pass
        item.setPixmap(pixmap)
        item.setPos(x, y)
        self.scene.addItem(item)
        # TODO: draw outline if selected