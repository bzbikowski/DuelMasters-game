from PySide6.QtCore import Qt
from PySide6.QtGui import QBrush, QColor, QPixmap, QPen, QFont
from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QGraphicsView, QGraphicsScene, \
    QGraphicsPixmapItem, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsRectItem, QDialog, \
    QInputDialog, QMessageBox


class ManagerCardHandle(QGraphicsPixmapItem):
    """
    Single card handle to check more info, add or remove card from your deck.
    """
    def __init__(self, id, parent):
        super(ManagerCardHandle, self).__init__()
        self.parent = parent
        self.id = id

    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.parent.pop_window(self.id)
            return
        if event.button() == Qt.LeftButton:
            if len(self.parent.deck) < 40:
                if self.parent.deck.count(self.id) < 4:
                    self.parent.deck.append(self.id)
        elif event.button() == Qt.RightButton:
            if self.id in self.parent.deck:
                index = self.parent.deck.index(self.id)
                self.parent.deck.pop(index)
        self.parent.redraw()