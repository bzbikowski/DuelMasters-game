from PySide6.QtWidgets import QGraphicsView
from PySide6.QtCore import QObject, Signal, Slot 


class DeckBuilder(QGraphicsView):
    """
    View representing all the cards in the deck. Scrolling through this view shows different cards in the database.
    """
    changeRow = Signal(int)

    def __init__(self, parent):
        super(DeckBuilder, self).__init__(parent)
        self.parent = parent

    def wheelEvent(self, event):
        wheel = event.angleDelta().y()
        if wheel > 0:
            self.changeRow.emit(-1)
        elif wheel < 0:
            self.changeRow.emit(1)