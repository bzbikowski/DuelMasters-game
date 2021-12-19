from PySide6.QtCore import QObject, Slot, Qt
from PySide6.QtGui import QCursor, QTransform, QPixmap, QAction
from PySide6.QtWidgets import QGraphicsScene, QGraphicsPixmapItem, QMenu, QWidget, QGraphicsView


class GraveyardView(QGraphicsView):
    """
    View representing all the cards in the graveyard. Scrolling through this view shows different cards in the database.
    """
    def __init__(self, parent):
        super(GraveyardView, self).__init__(parent)
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