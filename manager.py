from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QGraphicsView, QGraphicsScene, \
QGraphicsPixmapItem, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsRectItem, QScrollArea, QLabel, QTextEdit, \
QComboBox
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
        self.deck = []
        self.setFixedSize(1300, 500)
        self.parent = parent
        self.main_layout = QHBoxLayout(self)
        self.screen_layout = QVBoxLayout()
        self.button_layout = QHBoxLayout()
        self.deck_view = QGraphicsView(self)
        self.deck_view.setSceneRect(0, 0, 400, 400)
        self.deck_view.setFixedSize(440, 440)
        self.deck_view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.deck_scene = QGraphicsScene(self)
        self.deck_scene.setBackgroundBrush(QBrush(QColor(0, 0, 0)))
        self.deck_view.setScene(self.deck_scene)
        self.gui_layout = QVBoxLayout()
        self.build_gui()
        self.main_layout.addWidget(self.deck_view)
        self.main_layout.addLayout(self.screen_layout)
        self.main_layout.addLayout(self.gui_layout)
        self.database = ParseXml().parseFile("res//cards.xml")
        self.actual_view = range(len(self.database))
        self.view = DeckBuilder(self)
        self.view.setFixedSize(545, 365)
        self.view.setSceneRect(0, 0, 545, 365)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.canvas = QGraphicsScene(self)
        self.canvas.setBackgroundBrush(QBrush(QColor(0, 0, 0)))
        self.view.setScene(self.canvas)
        self.screen_layout.addWidget(self.view)
        self.screen_layout.addLayout(self.button_layout)
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

    def build_gui(self):
        self.search_layout = QHBoxLayout()
        self.gui_layout.addLayout(self.search_layout)
        self.search_label = QLabel("Wyszukaj", self)
        self.search_input = QTextEdit(self)
        self.search_layout.addWidget(self.search_label)
        self.search_layout.addWidget(self.search_input)

        self.civ_layout = QHBoxLayout()
        self.gui_layout.addLayout(self.civ_layout)
        self.civ_label = QLabel("Civilization", self)
        self.civ_input = QComboBox(self)
        self.civ_input.addItem("")
        self.civ_input.addItem("Light")
        self.civ_input.addItem("Water")
        self.civ_input.addItem("Darkness")
        self.civ_input.addItem("Fire")
        self.civ_input.addItem("Nature")
        self.civ_layout.addWidget(self.civ_label)
        self.civ_layout.addWidget(self.civ_input)

        self.search_button = QPushButton(self)
        self.search_button.clicked.connect(self.search_cards)
        self.gui_layout.addWidget(self.search_button)

    def search_cards(self):
        pass

    def search_by_name(self):
        name = self.search_input.toPlainText()
        if name == "":
            self.actual_view = range(len(self.database))
        else:
            self.actual_view = []
            for card in self.database:
                if name in card.name:
                    self.actual_view.append(card.id)
        self.actual_row = 0
        self.redraw()
    
    def search_by_civ(self):
        civ = self.civ_input.currentText()
        self.actual_view = []
        for card in self.database:
            if civ in card.civ:
                self.actual_view.append(card.id)
        self.actual_row = 0
        self.redraw()

    def redraw(self):
        self.canvas.clear()
        self.deck_scene.clear()
        offset = self.actual_row * self.row_size
        x = 5
        y = 5
        ind = 0
        for _ in range(self.column_size):
            for _ in range(self.row_size):
                if ind+offset < len(self.actual_view):
                    id = self.actual_view[offset+ind]
                    self.draw_card(x, y, id)
                    if id in self.deck:
                        self.draw_number(x, y, self.deck.count(id))
                    x += 90
                    ind += 1
            x = 5
            y += 120
        y = 2
        for card in self.deck:
            self.draw_result(y, card)
            y += 32

    def draw_card(self, x, y, id):
        card = CardHandle(id, self)
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

    def draw_result(self, y, id):
        rect = QGraphicsRectItem(10, y, 380, 30)
        rect.setPen(QPen(QColor(127, 127, 127)))
        self.deck_scene.addItem(rect)

        text = QGraphicsTextItem(self.database[id].name)
        text.setPos(10, y)
        text.setFont(QFont("Arial", 10))
        text.setDefaultTextColor(QColor(255, 0, 0))
        self.deck_scene.addItem(text)

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
        if wheel > 0:
            if self.parent.actual_row > 0:
                self.parent.actual_row -= 1
        elif wheel < 0:
            if len(self.parent.actual_view) > (self.parent.actual_row+1) * self.parent.row_size:
                self.parent.actual_row += 1
        else:
            print("Excuse me")
        self.parent.redraw()

class CardHandle(QGraphicsPixmapItem):
    def __init__(self, id, parent):
        super(CardHandle, self).__init__()
        self.parent = parent
        self.id = id

    def mousePressEvent(self, event):
        if len(self.parent.deck) < 40:
            if event.button() == Qt.LeftButton:
                if self.parent.deck.count(self.id) < 4:
                    self.parent.deck.append(self.id)
            elif event.button() == Qt.RightButton:
                if self.id in self.parent.deck:
                    index = self.parent.deck.index(self.id)
                    self.parent.deck.pop(index)
            self.parent.redraw()