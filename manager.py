from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QGraphicsEllipseItem, QGraphicsTextItem
from PyQt5.QtGui import QBrush, QColor, QPixmap, QPen, QFont
from PyQt5.QtCore import Qt
from cards import ParseXml, Card
import os

class DeckManager(QWidget):
    """
    todo wyświetlenie kart, sortowanie, wyszukiwarka
    """
    def __init__(self, parent=None):
        super(DeckManager, self).__init__()
        self.deck = [0,0,0,0,0,1,1,1,1,2,2,2,3,3,4]
        self.setFixedSize(575, 450)
        self.parent = parent
        self.main_layout = QVBoxLayout(self)
        self.button_layout = QHBoxLayout()
        self.database = ParseXml().parseFile("res//cards.xml")
        self.view = DeckBuilder(self)
        self.view.setFixedSize(545, 365)
        self.view.setSceneRect(0, 0, 545, 365)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.canvas = QGraphicsScene(self)
        self.canvas.setBackgroundBrush(QBrush(QColor(0, 0, 0)))
        self.view.setScene(self.canvas)
        self.main_layout.addWidget(self.view)
        self.main_layout.addLayout(self.button_layout)
        self.save_button = QPushButton("Save", self)
        self.clear_button = QPushButton("Clear", self)
        self.exit_button = QPushButton("Exit", self)
        self.exit_button.clicked.connect(self.exit)
        self.button_layout.addWidget(self.save_button)
        self.button_layout.addWidget(self.clear_button)
        self.button_layout.addWidget(self.exit_button)
        self.actual_row = 0
        self.row_size = 6
        self.column_size = 3
        self.redraw()

    def redraw(self):
        id = self.actual_row * self.row_size
        x = 5
        y = 5
        for _ in range(self.column_size):
            for _ in range(self.row_size): 
                self.draw_card(x, y, id)
                if id in self.deck:
                    self.draw_number(x, y, self.deck.count(id))
                x += 90
                id += 1
            x = 5
            y += 120

    def draw_card(self, x, y, id):
        card = CardHandle()
        if os.path.exists(self.database[id].image):
            card.setPixmap(QPixmap(self.database[id].image))
        else:
            card.setPixmap(QPixmap("res//img//cardback.png"))
        card.setPos(x, y)
        self.canvas.addItem(card)

    def draw_number(self, x, y, number):
        elipse = QGraphicsEllipseItem(x+24, y+35, 40, 40)
        elipse.setBrush(QBrush(QColor(255, 255, 255)))
        pen = QPen()
        pen.setColor(QColor(255, 0, 0))
        pen.setWidth(5)
        elipse.setPen(pen)
        self.canvas.addItem(elipse)

        numb = QGraphicsTextItem(str(number))
        numb.setPos(x+27, y+30)
        numb.setFont(QFont("Arial", 30))
        numb.setDefaultTextColor(QColor(255, 0, 0))
        self.canvas.addItem(numb)

    def clear_deck(self):
        self.deck = []

    def save_deck(self):
        self.parent.deck = self.deck

    def exit(self):
        self.parent.show_window()
        self.close()

    def closeEvent(self, event):
        self.parent.show_window()


class DeckBuilder(QGraphicsView):
    def __init__(self, parent):
        super(DeckBuilder, self).__init__(parent)
        self.parent = parent

    def wheelEvent(self, event):
        wheel = event.angleDelta().y()
        if wheel < 0:
            self.parent.actual_row -= 1
        elif wheel > 0:
            self.parent.actual_row += 1
        else:
            print("Excuse me")
        self.parent.redraw()

class CardHandle(QGraphicsPixmapItem):
    def __init__(self):
        super(CardHandle, self).__init__()

    def mousePressEvent(self, event):
        pass

    def mouseReleaseEvent(self, event):
        pass