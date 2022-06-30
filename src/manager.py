import os
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QBrush, QColor, QPixmap, QPen, QFont
from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QGraphicsView, QGraphicsScene, \
    QGraphicsPixmapItem, QGraphicsEllipseItem, QGraphicsTextItem, QGraphicsRectItem, QDialog, \
    QInputDialog, QMessageBox, QFileDialog

from src.ui.ui_manager import Ui_Manager
from src.views.manager import ManagerCardHandle


class DeckManager(QWidget):
    """
    Deck manager, which is used to create, save your own deck
    """

    def __init__(self, database, parent=None, deck=None):
        """
        deck - if set, open pre-loaded deck to edit
        """
        super(DeckManager, self).__init__()
        if deck is not None:
            self.deck = deck
        else:
            self.deck = []
        self.parent = parent
        self.row_size = 0
        self.column_size = 0
        self.ui = Ui_Manager()
        self.ui.setupUi(self)
        self.setup_all_components()
        self.database = database
        self.actual_view = range(self.database.count())
        self.actual_row = 0

        self.redraw()

    def setup_all_components(self):
        """
        Build all components of the GUI
        """
        self.setWindowState(Qt.WindowMaximized)

        deck_view_width = int(self.width() * 0.4)
        deck_view_height = self.height()
        # self.ui.deck_view.setFixedSize(deck_view_width, deck_view_height)
        self.ui.deck_view.setSceneRect(0, 0, deck_view_width, deck_view_height)

        self.deck_scene = QGraphicsScene(self)
        self.deck_scene.setBackgroundBrush(QBrush(QColor(0, 0, 0)))
        self.ui.deck_view.setScene(self.deck_scene)

        self.ui.type_input.addItem("All")
        self.ui.type_input.addItem("Creature")
        self.ui.type_input.addItem("Spell")

        self.ui.civ_input.addItem("All")
        self.ui.civ_input.addItem("Light")
        self.ui.civ_input.addItem("Water")
        self.ui.civ_input.addItem("Darkness")
        self.ui.civ_input.addItem("Fire")
        self.ui.civ_input.addItem("Nature")

        self.ui.power_option.addItem("<=")
        self.ui.power_option.addItem("==")
        self.ui.power_option.addItem(">=")

        self.ui.search_button.clicked.connect(self.search_cards)

        view_width = int(self.width() * 0.4)
        view_height = self.height()

        self.row_size = view_width // 100
        self.column_size = view_height // 130


        # self.ui.view.setFixedSize(view_width, view_height)
        self.ui.view.setSceneRect(0, 0, view_width, view_height)
        self.ui.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.ui.view.changeRow.connect(self.handleDeckbuilderRowChanged)

        self.canvas = QGraphicsScene(self)
        self.canvas.setBackgroundBrush(QBrush(QColor(0, 0, 0)))
        self.ui.view.setScene(self.canvas)

        self.ui.save_button.clicked.connect(self.save_deck)
        self.ui.clear_button.clicked.connect(self.clear_deck)
        self.ui.exit_button.clicked.connect(self.exit)

    def search_cards(self):
        """
        Search engine, check all cards in database if they pass all requirements
        """
        self.actual_view = range(self.database.count())
        name = self.ui.name_input.text()
        if not name == "":
            self.actual_view = self.search_by_name(name)
        typ = self.ui.type_input.currentText()
        if not typ == "All":
            self.actual_view = self.search_by_type(typ)
        civ = self.ui.civ_input.currentText()
        if not civ == "All":
            self.actual_view = self.search_by_civ(civ)
        cost = self.ui.cost_input.text()
        if not cost == "":
            try:
                cost = int(cost)
            except ValueError:
                self.actual_view = range(self.database.count())
                _ = QMessageBox.information(self, "Information", "Wrong cost value.",
                                    QMessageBox.Ok, QMessageBox.NoButton)
                return
            self.actual_view = self.search_by_cost(cost)
        power = self.ui.power_input.text()
        sign = self.ui.power_option.currentText()
        if not power == "":
            try:
                power = int(power)
            except ValueError:
                self.actual_view = range(self.database.count())
                _ = QMessageBox.information(self, "Information", "Wrong power value.",
                                    QMessageBox.Ok, QMessageBox.NoButton)
                return
            self.actual_view = self.search_by_power(power, sign)
        self.actual_row = 0
        self.redraw()

    def search_by_name(self, name):
        """
        Check if string name is in actual card name
        """
        view = []
        for card in self.actual_view:
            if str.lower(name) in str.lower(self.parent.database.get_data(card, 'name')):
                view.append(card)
        return view

    def search_by_type(self, typ):
        """
        Check type of the card
        """
        view = []
        for card in self.actual_view:
            if typ == self.parent.database.get_data(card, "type"):
                view.append(card)
        return view

    def search_by_civ(self, civ):
        """
        Check civilization of the card
        """
        view = []
        for card in self.actual_view:
            if civ in self.parent.database.get_data(card, "civilization"):
                view.append(card)
        return view

    def search_by_power(self, power, sign):
        """
        Check if power of the creature is less/eual/greater than ... power 
        """
        view = []
        for card in self.actual_view:
            card_power = self.parent.database.get_data(card, "power")
            card_type = self.parent.database.get_data(card, "type")
            if card_type == "Spell":
                continue
            if sign == "<=":
                if power >= card_power:
                    view.append(card)
            elif sign == "==":
                if power == card_power:
                    view.append(card)
            elif sign == ">=":
                if 0 < power <= card_power:
                    view.append(card)
        return view

    def search_by_cost(self, cost):
        """
        Check cost of the card
        Todo: maybe add less/equal/greater
        """
        view = []
        for card in self.actual_view:
            if cost == self.parent.database.get_data(card, "cost"):
                view.append(card)
        return view

    def redraw(self):
        """
        Redraw all the elements on the GraphicsScene
        """
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
            self.draw_result(y, card, card_dict[card], self.parent.database.get_data(card, 'civilization'))
            y += 32
            if y > 400:
                self.ui.deck_view.setSceneRect(0, 0, 400, y)
            else:
                self.ui.deck_view.setSceneRect(0, 0, 400, 400)

    def draw_card(self, x, y, id):
        """
        Draw card item with its image on the screen
        """
        card = ManagerCardHandle(id, self)
        pixmap = QPixmap()
        if not pixmap.loadFromData(self.parent.database.get_data(id, 'low_res')):
            pass
        card.setPixmap(pixmap)
        card.setPos(x, y)
        self.canvas.addItem(card)

    def draw_number(self, x, y, number):
        """
        Draw number of card in the deck on the screen
        """
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
        """
        Draw informations about card that is in the deck
        """
        palette = {"Nature": QColor(0, 255, 0), "Fire": QColor(255, 0, 0), "Water": QColor(0, 0, 255), "Light": QColor(255, 255, 0)
                   , "Darkness": QColor(128, 128, 128)}
        rect = QGraphicsRectItem(10, y, 380, 30)
        rect.setPen(QPen(QColor(127, 127, 127)))
        self.deck_scene.addItem(rect)

        text = QGraphicsTextItem("{0} x {1}".format(count, self.parent.database.get_data(id, "name")))
        text.setPos(10, y)
        text.setFont(QFont("Arial", 10))
        text.setDefaultTextColor(palette[civ])
        self.deck_scene.addItem(text)

    def pop_window(self, card_id):
        """
        Show card image in better resolution
        """
        self.info_window = CardInfo(self, self.parent.database.get_data(card_id, "high_res"))
        self.info_window.show()

    def clear_deck(self):
        if len(self.deck) > 0:
            button = QMessageBox.information(self, "Information", "Are you sure you want to clear your deck?", QMessageBox.Ok, QMessageBox.Cancel)
            if button == QMessageBox.Ok:
                self.deck = []
                self.ui.deck_view.setSceneRect(0, 0, 400, 400)
                self.redraw()

    def save_deck(self):
        if len(self.deck) < 40:
            button = QMessageBox.information(self, "Information", "Your deck is incomplete. Do you want to continue?",
                                         QMessageBox.Ok, QMessageBox.Cancel)
            if button == QMessageBox.Cancel:
                return
        deck_file = QFileDialog().getSaveFileName(self, "Save deck", os.path.join(os.path.dirname(__file__), os.pardir, "decks"), "Text files (*.txt)")
        if not deck_file or deck_file[0] == "":
            return
        deck_file = deck_file[0]
        if not deck_file.endswith(".txt"):
            deck_file += ".txt"
        check = self.validate_file_name(deck_file)
        if check:
            with open(deck_file, "w") as f:
                for card in self.deck:
                    f.write("{0}\n".format(card))
        else:
            _ = QMessageBox.information(self, "Information", "Incorrect file name.",
                                             QMessageBox.Ok, QMessageBox.NoButton)

    @Slot(int)
    def handleDeckbuilderRowChanged(self, direction):
        if direction == -1:
            if self.actual_row > 0:
                self.actual_row -= 1
        elif direction == 1:
            if len(self.actual_view) > (self.actual_row+1) * self.row_size:
                self.actual_row += 1
        self.redraw()

    @staticmethod
    def validate_file_name(path):
        """
        Check string if it's acceptable for file name
        """
        deck_name = os.path.basename(path)
        chars = ["!", "/", "?"]
        for char in chars:
            if char in deck_name:
                return False
        return True

    def exit(self):
        self.parent.show_window()
        self.close()

    def closeEvent(self, event):
        self.parent.show_window()


class CardInfo(QDialog):
    """
    Window for showing card image in better resolution
    """
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
        pixmap = QPixmap()
        if not pixmap.loadFromData(card):
            pass
        self.image = QGraphicsPixmapItem(pixmap)
        self.image.setPos(0, 0)
        self.scene.addItem(self.image)
