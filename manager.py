from PyQt5.QtWidgets import QWidget, QPushButton, QVBoxLayout, QHBoxLayout, QGraphicsView, QGraphicsScene, \
QGraphicsPixmapItem, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsRectItem, QScrollArea, QLabel, QTextEdit, \
QComboBox, QDialog, QInputDialog
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
        self.save_button.clicked.connect(self.save_deck)
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
        self.name_layout = QHBoxLayout()
        self.gui_layout.addLayout(self.name_layout)
        self.name_label = QLabel("Name", self)
        self.name_input = QTextEdit(self)
        self.name_layout.addWidget(self.name_label)
        self.name_layout.addWidget(self.name_input)

        self.type_layout = QHBoxLayout()
        self.gui_layout.addLayout(self.type_layout)
        self.type_label = QLabel("Type", self)
        self.type_input = QComboBox(self)
        self.type_input.addItem("")
        self.type_input.addItem("Creature")
        self.type_input.addItem("Spell")
        self.type_layout.addWidget(self.type_label)
        self.type_layout.addWidget(self.type_input)

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

        self.cost_layout = QHBoxLayout()
        self.gui_layout.addLayout(self.cost_layout)
        self.cost_label = QLabel("Cost", self)
        self.cost_input = QTextEdit(self)
        self.cost_layout.addWidget(self.cost_label)
        self.cost_layout.addWidget(self.cost_input)

        self.power_layout = QHBoxLayout()
        self.gui_layout.addLayout(self.power_layout)
        self.power_label = QLabel("Power", self)
        self.power_option1 = QComboBox(self)
        self.power_option1.addItem("<=")
        self.power_option1.addItem("==")
        self.power_option1.addItem(">=")
        self.power_input1 = QTextEdit(self)
        self.power_layout.addWidget(self.power_label)
        self.power_layout.addWidget(self.power_option1)
        self.power_layout.addWidget(self.power_input1)

        self.search_button = QPushButton("Search", self)
        self.search_button.clicked.connect(self.search_cards)
        self.gui_layout.addWidget(self.search_button)

    def search_cards(self):
        self.actual_view = range(len(self.database))
        name = self.name_input.toPlainText()
        if not name == "":
            self.actual_view = self.search_by_name(name)
        typ = self.type_input.currentText()
        if not typ == "":
            self.actual_view = self.search_by_type(typ)
        civ = self.civ_input.currentText()
        if not civ == "":
            self.actual_view = self.search_by_civ(civ)
        cost = self.cost_input.toPlainText()
        if not cost == "":
            try:
                cost = int(cost)
            except ValueError:
                return
            self.actual_view = self.search_by_cost(cost)
        power = self.power_input1.toPlainText()
        sign = self.power_option1.currentText()
        if not power == "":
            try:
                power = int(power)
            except ValueError:
                return
            self.actual_view = self.search_by_power(power, sign)
        self.actual_row = 0
        self.redraw()

    def search_by_name(self, name):
        view = []
        for card in self.actual_view:
            if name in self.database[card].name:
                view.append(card)
        return view

    def search_by_type(self, typ):
        view = []
        for card in self.actual_view:
            if typ == self.database[card].typ:
                view.append(card)
        return view

    def search_by_civ(self, civ):
        view = []
        for card in self.actual_view:
            if civ in self.database[card].civ:
                view.append(card)
        return view

    def search_by_power(self, power, sign):
        view = []
        for card in self.actual_view:
            card_power = int(self.database[card].power)
            if sign == ">=":
                if power >= card_power:
                    view.append(card)
            elif sign == "==":
                if power == card_power:
                    view.append(card)
            elif sign == "<=":
                if power >= card_power > 0:
                    view.append(card)
        return view

    def search_by_cost(self, cost):
        view = []
        for card in self.actual_view:
            if cost == int(self.database[card].cost):
                view.append(card)
        return view

    def redraw(self):
        self.canvas.clear()
        self.deck_scene.clear()
        self.parent.deck = self.deck
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
        card_dict = {}
        for card in self.deck:
            if card not in card_dict:
                card_dict[card] = 1
            else:
                card_dict[card] += 1

        for card in card_dict.keys():
            self.draw_result(y, card, card_dict[card], self.database[card].civ)
            y += 32
            if y > 400:
                self.deck_view.setSceneRect(0, 0, 400, y)
            else:
                self.deck_view.setSceneRect(0, 0, 400, 400)

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

    def draw_result(self, y, id, count, civ):
        palette = {"Nature": QColor(0, 255, 0), "Fire": QColor(255, 0, 0), "Water": QColor(0, 0, 255), "Light": QColor(255, 255, 0)
                   , "Darkness": QColor(128, 128, 128)}
        rect = QGraphicsRectItem(10, y, 380, 30)
        rect.setPen(QPen(QColor(127, 127, 127)))
        self.deck_scene.addItem(rect)

        text = QGraphicsTextItem("{0} x {1}".format(count, self.database[id].name))
        text.setPos(10, y)
        text.setFont(QFont("Arial", 10))
        text.setDefaultTextColor(palette[civ])
        self.deck_scene.addItem(text)

    def pop_window(self, card_id):
        self.info_window = CardInfo(self, self.database[card_id])
        self.info_window.show()

    def clear_deck(self):
        self.deck = []

    def save_deck(self):
        name, okpressed = QInputDialog.getText(self, "Name your deck", "Name")
        if not okpressed:
            return
        with open("decks/{}.txt".format(name), "w") as f:
            for card in self.deck:
                f.write("{0}\n".format(card))

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
        if event.button() == Qt.MidButton:
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


class CardInfo(QDialog):
    def __init__(self, parent, card):
        super(CardInfo, self).__init__(parent)
        self.setFixedSize(400, 600)
        self.main_layout = QVBoxLayout(self)
        self.view = QGraphicsView(self)
        self.view.setFixedSize(365, 515)
        self.view.setSceneRect(0, 0, 350, 500)
        self.main_layout.addWidget(self.view)
        self.scene = QGraphicsScene(self)
        self.view.setScene(self.scene)

        self.draw_info(card)

        self.exit_button = QPushButton("Exit", self)
        self.exit_button.clicked.connect(self.close)
        self.main_layout.addWidget(self.exit_button)

    def draw_info(self, card):
        self.image = QGraphicsPixmapItem(QPixmap(card.info))
        self.image.setPos(0, 0)
        self.scene.addItem(self.image)
