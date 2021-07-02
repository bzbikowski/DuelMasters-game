from PySide2.QtWidgets import QGraphicsView

class DeckBuilder(QGraphicsView):
    """
    View representing all the cards in the deck. Scrolling through this view shows different cards in the database.
    """
    def __init__(self, parent):
        super(DeckBuilder, self).__init__(parent)
        self.parent = parent

    def wheelEvent(self, event):
        wheel = event.angleDelta().y()
        if wheel > 0:
            if self.parent.actual_row > 0:
                self.parent.actual_row -= 1
        elif wheel < 0:
            if len(self.parent.actual_view) > (self.parent.actual_row+1) * self.parent.row_size:
                self.parent.actual_row += 1
        self.parent.redraw()