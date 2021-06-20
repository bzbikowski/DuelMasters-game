import logging
import random

from PySide2.QtCore import Qt, QTimer, QThread, Slot, Signal
from PySide2.QtGui import QBrush, QColor, QPen, QPixmap, QTransform, QImage, QFont
from PySide2.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, \
    QTextEdit, QLabel, QPushButton, QGraphicsRectItem, QGraphicsTextItem, QMessageBox

from src.logs import Logger
from src.network.client import Client
from src.network.server import Server
from src.views import GameView, CardView, GraveyardView
from src.dialog import ServerDialog, ClientDialog
from src.controller import Controller
from src.ui.ui_game import Ui_Game
from src.zones import Battlezone, Graveyardzone, Handzone, Manazone, Shieldzone, Spellzone


class Game(QWidget):
    """
    Main class in application.
    """
    def __init__(self, mode, deck, database, debug, parent=None):
        super(Game, self).__init__()
        self.ui = Ui_Game()
        self.ui.setupUi(self)
        self.log = None
        self.mode = mode
        self.database = database
        # self.move((screen_width - self.width)/2, (screen_height - self.height)/2 - 20)
        self.debug_mode = debug
        self.locked = False
        self.isServer = False
        self.started = False
        self.parent = parent
        self.deck = deck
        self.card_to_draw = 0
        self.card_to_mana = 0
        self.your_turn = 0 # 0 - not your turn, 1 - your turn, 2 - special turn, 3 - block or pass creature, 4 - block or pass shield, 5 - shield destroyed
        self.selected_card = None
        self.focus_request = False
        self.select_mode = 0  # 0 - no select mode, 1 - effects, 2 - creature, 21 - shields attack
        self.card_to_choose = 0
        self.turn_count = 0
        self.spell_played = None

        self.view_scene = GameView(self)
        self.ui.view.setScene(self.view_scene)
        self.view_scene.setBackgroundBrush(QBrush(QColor(0, 0, 0)))

        self.preview_scene = QGraphicsScene()
        self.ui.preview.setScene(self.preview_scene)
        self.preview_scene.setBackgroundBrush(QBrush(QColor(0, 0, 0)))

        self.log_panel = Logger()
        self.setup_logger()

        self.controller = Controller(self)

        if self.mode == 1:
            self.wait_for_connection()
        else:
            self.connect_to_room()

    ## Internal
    def setup_logger(self):
        self.log = logging.getLogger("dm_game")
        if self.debug_mode:
            self.log.setLevel(logging.DEBUG)
        else:
            self.log.setLevel(logging.INFO)

    def closeEvent(self, event):
        """Close connection and return to menu"""
        if self.started:
            if self.mode == 1:
                try:
                    self.server.close_connection()
                except RuntimeError:
                    self.log.debug("Server already closed.")
            else:
                try:
                    self.client.disconnectFromHost()
                except RuntimeError:
                    self.log.debug("Client already closed.")
        self.parent.show_window()

    def handle_disconnect(self):
        print("GAME - DISCONNECTED")
        self.close()

    def handle_error(self):
        print("GAME - ERROR")
        self.close()

    ## Game initialize functions - setup network connection
    def connect_to_room(self):
        """
        Client side
        Enter ip address and port of computer, which you want to connect to
        """
        self.clientDialog = ClientDialog()
        self.clientDialog.closing.connect(self.close)
        self.clientDialog.paramsReady.connect(self.start_connection)
        self.clientDialog.show()
        self.log.debug("Connecting to server...")

    @Slot(str, str)
    def start_connection(self, ip_address, port):
        """
        Client side
        Connect with the server
        """
        self.clientDialog.close()
        self.isServer = False
        self.client = Client(ip_address, port, self)
        self.client.connected.connect(self.connected_with_player)
        self.client.disconnected.connect(self.handle_disconnect)
        self.client.error.connect(self.handle_error)
        self.client.messageReceived.connect(self.controller.received_message)
        self.client.run()
        self.started = True

    def wait_for_connection(self):
        """
        Server side
        Wait for connection from other client.
        """
        self.server = Server(self)
        self.server.connectionOk.connect(self.connected_with_player)
        self.server.messageReceived.connect(self.controller.received_message)
        self.server.clientError.connect(self.close)

        self.serverDialog = ServerDialog()
        self.serverDialog.closing.connect(self.close)

        ip_local, ip_port = self.server.find_ip()
        if ip_local == "0.0.0.0":
            _ = QMessageBox.information(self, "Information", "Couldn't find a valid ip address."
                                                             " Please check your connection.",
                                        QMessageBox.Ok, QMessageBox.NoButton)
            return
        else:
            self.serverDialog.ui.ip_address_label.setText("Your address is {}".format(ip_local))
            self.serverDialog.ui.port_label.setText("You are listining on port {}".format(ip_port))
            self.serverDialog.ui.status_label.setText("Waiting for connection...")

        self.server.run()
        self.started = True
        self.serverDialog.show()

    def connected_with_player(self):
        """
        Connection is successful, start actual game
        """
        try:
            self.serverDialog.close()
        except:
            self.log.debug(f"Client mode, so server dialog was not open and can't be closed.")
        self.show()
        self.log.info("Found opponent. Game is being started.")
        if self.mode == 1:
            if random.random() < 0.5:
                self.send_message(0)
                self.turn_states(0)
                self.add_log("You start the game! Your turn.", False)
                self.log.info(f"Turn {self.turn_count}: Host turn.")
            else:
                self.send_message(1)
                self.add_log("Opponent starts the game.", False)
                self.log.info(f"Turn {self.turn_count}: Opponent turn.")
        self.init_game()
        self.draw_screen()

    ## Game functions
    def init_game(self):
        """
        Create initial structures and data for our starting game
        """
        self.log.debug(f"Initializing variables.")

        self.shields = Shieldzone()
        self.hand = Handzone()
        self.mana = Manazone()
        self.bfield = Battlezone()
        self.sfield = Spellzone()
        self.graveyard = Graveyardzone()

        self.opp_shields = Shieldzone(opponent=True)
        self.opp_mana = Manazone(opponent=True)
        self.opp_hand = Handzone(opponent=True)
        self.opp_bfield = Battlezone(opponent=True)
        self.opp_sfield = Spellzone(opponent=True)
        self.opp_graveyard = Graveyardzone(opponent=True)

        random.shuffle(self.deck)
        for card_id in self.deck[0:5]:
            self.shields.add_shield(self.database.get_card(card_id))
            self.opp_shields.add_placeholder()
        for card_id in self.deck[5:10]:
            self.hand.add_card(self.database.get_card(card_id))
            self.opp_hand.add_placeholder()
        self.deck = self.deck[10:]

        # Load assets into the game
        background_pixmap = QPixmap()
        background_pixmap.loadFromData(self.database.get_asset("background"))
        self.background = QGraphicsPixmapItem(background_pixmap) # Needed
        self.view_scene.addItem(self.background)

        preview_pixmap = QPixmap()
        preview_pixmap.loadFromData(self.database.get_asset("preview"))
        self.preview_scene.addItem(QGraphicsPixmapItem(preview_pixmap))

        self.cardback_pixmap = QPixmap()
        self.cardback_pixmap.loadFromData(self.database.get_asset("cardback"))

        self.lock_pixmap = QPixmap()
        self.lock_pixmap.loadFromData(self.database.get_asset("lock"))

        self.extend_logs_button = QPushButton()
        self.extend_logs_button.setFixedSize(20, 20)
        self.extend_logs_button.clicked.connect(self.change_logs_size)
        self.extend_logs_proxy = self.preview_scene.addWidget(self.extend_logs_button)

        self.change_button_state = True
        self.spell_played = False
        self.selected_card = []
        self.selected_shields = []
        self.fun_queue = []

    def start_time(self):
        """
        Implemented to block choosing multiple cards with one click.
        One mouse click should always choose a card on the top.
        """
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(20)
        self.timer.start()
        self.timer.timeout.connect(self.change_state)

    def change_state(self):
        """Change state"""
        self.locked = False
        
    def draw_screen(self):
        """
        Draw all elements into the screen.
        """
        # your shields
        self.add_shields_to_scene("yu_sh")
        # opponent's shields
        self.add_shields_to_scene("op_sh")
        # your battlefield
        self.add_bf_to_scene("yu_bf")
        # opponent's battlefield
        self.add_bf_to_scene("op_bf")
        # your spell field
        self.add_sf_to_scene("yu_sf")
        # opponent's spell field
        self.add_sf_to_scene("op_sf")
        # your graveyard
        self.add_graveyard_to_scene("yu_gv")
        # opponent's graveyard
        self.add_graveyard_to_scene("op_gv")
        # your cards in hand
        self.add_hand_to_scene("yu_hd")
        # opponent's cards in hand
        self.add_hand_to_scene("op_hd")
        # your cards in mana zone
        self.add_mana_to_scene("yu_mn")
        # opponent's cards in mana zone
        self.add_mana_to_scene("op_mn")
        # change max number of logs to display
        size_of_panel = len(self.log_panel)
        if self.change_button_state:
            self.extend_logs_button.setText("+")
            if size_of_panel < 3:
                self.extend_logs_proxy.setPos(20, 728 - size_of_panel * 60)
            else:
                self.extend_logs_proxy.setPos(20, 540)
        else:
            self.extend_logs_button.setText("-")
            self.extend_logs_proxy.setPos(20, 20)
        # display logs
        if size_of_panel > 0:
            if self.change_button_state:
                lenght = min(len(self.log_panel), 3)
            else:
                lenght = min(len(self.log_panel), 10)
            x_pos = 20
            y_pos = 698
            y_height = 50
            x_width = 296
            for i in range(lenght):
                log = self.log_panel[i]
                frame = QGraphicsRectItem(x_pos, y_pos, x_width, y_height)
                frame.setPen(QPen(QColor(255, 0, 0)))
                self.preview_scene.addItem(frame)

                text = QGraphicsTextItem(log)
                text.setPos(x_pos + 10, y_pos + 5)
                text.setTextWidth(x_width-20)
                self.preview_scene.addItem(text)
                y_pos -= 60

    def get_pixmap_card(self, card_id, res='low_res'):
        """Get pixmap of card from the database"""
        pixmap = QPixmap()
        if not pixmap.loadFromData(self.database.get_data(card_id, res)):
            self.log.error(f"No image available for card {card_id}")
            exit(0)
        return pixmap
        
    def card_clicked(self, x, y, c_id=None):
        """
        Display info and highlight a card when it is clicked on the board
        """
        self.refresh_screen()
        if self.change_button_state:
            if c_id is not None:
                self.draw_preview_card(c_id)
        self.highlight_card(x, x + 85, y, y + 115, QColor(255, 0, 0))

    def change_logs_size(self):
        """Change size of log panel on right size"""
        self.change_button_state = not self.change_button_state
        self.refresh_screen()

    def highlight_card(self, x1, x2, y1, y2, color):
        """
        Draw a frame around a clicked card on the board
        """
        self.view_scene.addLine(x1 - 1, y1 - 1, x1 - 1, y2 + 1, QPen(color))
        self.view_scene.addLine(x2 + 1, y1 - 1, x2 + 1, y2 + 1, QPen(color))
        self.view_scene.addLine(x1 - 1, y1 - 1, x2 + 1, y1 - 1, QPen(color))
        self.view_scene.addLine(x1 - 1, y2 + 1, x2 + 1, y2 + 1, QPen(color))

    def draw_preview_card(self, card_id):
        """
        Draw a preview of the clicked card on preview side of the screen
        """
        pixmap = self.get_pixmap_card(card_id, 'medium_res')
        card_prev = QGraphicsPixmapItem(pixmap)
        card_prev.setPos(0, 0)
        self.preview_scene.addItem(card_prev)
        
    def add_hand_to_scene(self, type):
        """
        Draw card from hand into the screen
        """
        if type == "yu_hd":
            y = 639
            size_of_hand = len(self.hand)
            for i in range(size_of_hand):
                item = CardView(type, i, self)
                if self.hand.is_hidden(i):
                    pixmap = self.cardback_pixmap
                else:
                    pixmap = self.get_pixmap_card(self.hand[i].id)
                    item.set_card(self.hand[i])
                item.setPixmap(pixmap)
                if size_of_hand <= 6:
                    if size_of_hand % 2 == 0:
                        x = 422 - 95 * (size_of_hand/2 - 1) + i * 95
                        item.setPos(422 - 95 * (size_of_hand/2 - 1) + i * 95, y)
                    else:
                        x = 512 - 85 / 2 - 95 * ((size_of_hand - 1) / 2) + 95 * i
                        item.setPos(512 - 85 / 2 - 95 * ((size_of_hand - 1) / 2) + 95 * i, y)
                else:
                    x = 232 + (475 / (size_of_hand - 1)) * i
                    item.setPos(x, y)
                self.view_scene.addItem(item)
                if not len(self.selected_card) == 0:
                    for sel_card in self.selected_card:
                        if sel_card[0] == type:
                            if sel_card[1] == i:
                                self.highlight_card(x, x + 85, y, y + 115, QColor(0, 0, 255))
                                break
        elif type == "op_hd":
            y = 14
            size_of_hand = len(self.opp_hand)
            for i in range(size_of_hand):
                item = CardView(type, i, self)
                if self.opp_hand[i].is_placeholder():
                    pixmap = self.cardback_pixmap
                else:
                    pixmap = self.get_pixmap_card(self.opp_hand[i].id)
                    item.set_card(self.opp_hand[i])
                transform = QTransform().rotate(180)
                pixmap = pixmap.transformed(transform)
                item.setPixmap(pixmap)
                if size_of_hand <= 6:
                    if size_of_hand % 2 == 0:
                        x = 422 - 95 * (size_of_hand/2 - 1) + i * 95
                    else:
                        x = 512 - 85 / 2 - 95 * ((size_of_hand - 1) / 2) + 95 * i
                else:
                    x = 232 + (475 / (size_of_hand - 1)) * i
                item.setPos(x, y)
                self.view_scene.addItem(item)
                if not len(self.selected_card) == 0:
                    for sel_card in self.selected_card:
                        if sel_card[0] == type:
                            if sel_card[1] == i:
                                self.highlight_card(x, x + 85, y, y + 115, QColor(0, 0, 255))
                                break
            
    def add_mana_to_scene(self, type):
        """
        Draw card from mana into the screen
        """
        if type == "yu_mn":
            y = 514
            size_of_mana = len(self.mana)
            for i in range(size_of_mana):
                item = CardView(type, i, self)
                item.set_card(self.mana[i])
                pixmap = self.get_pixmap_card(self.mana[i].id)
                transform = QTransform().rotate(180)
                pixmap = pixmap.transformed(transform)
                if self.mana.is_tapped(i): # if selected, gray colors
                    image = pixmap.toImage()
                    image = image.convertToFormat(QImage.Format_Grayscale8)
                    pixmap = pixmap.fromImage(image)
                item.setPixmap(pixmap)
                if size_of_mana <= 6:
                    if size_of_mana % 2 == 0:
                        x = 422 - 95 * (size_of_mana/2 - 1) + i * 95
                    else:
                        x = 512 - 85 / 2 - 95 * ((size_of_mana - 1) / 2) + 95 * i
                else:
                    x = 232 + (475 / (size_of_mana - 1)) * i
                item.setPos(x, y)
                self.view_scene.addItem(item)
                if self.mana.is_locked(i): # if locked, add lock image
                    lock_item = QGraphicsPixmapItem(self.lock_pixmap)
                    lock_item.setPos(x + 10, y + 10)
                    self.view_scene.addItem(lock_item)
                if not len(self.selected_card) == 0:
                    for sel_card in self.selected_card:
                        if sel_card[0] == type:
                            if sel_card[1] == i:
                                self.highlight_card(x, x + 85, y, y + 115, QColor(0, 0, 255))
                                break
        elif type == "op_mn":
            y = 139
            size_of_mana = len(self.opp_mana)
            for i in range(size_of_mana):
                item = CardView(type, i, self)
                card = self.opp_mana[i]
                item.set_card(card)
                pixmap = self.get_pixmap_card(card.id)
                if self.opp_mana.is_tapped(i):
                    image = pixmap.toImage()
                    image = image.convertToFormat(QImage.Format_Grayscale8)
                    pixmap = pixmap.fromImage(image)
                item.setPixmap(pixmap)
                if size_of_mana <= 6:
                    if size_of_mana % 2 == 0:
                        x = 422 - 95 * (size_of_mana/2 - 1) + i * 95
                    else:
                        x = 512 - 85 / 2 - 95 * ((size_of_mana - 1) / 2) + 95 * i
                else:
                    x = 232 + (475 / (size_of_mana - 1)) * i
                item.setPos(x, y)
                self.view_scene.addItem(item)
                if self.opp_mana.is_locked(i): # if locked, add lock image
                    lock_item = QGraphicsPixmapItem(self.lock_pixmap)
                    lock_item.setPos(x + 10, y + 10)
                    self.view_scene.addItem(lock_item)
                if not len(self.selected_card) == 0:
                    for sel_card in self.selected_card:
                        if sel_card[0] == type:
                            if sel_card[1] == i:
                                self.highlight_card(x, x + 85, y, y + 115, QColor(0, 0, 255))
                                break

    def add_shields_to_scene(self, type):
        """
        Draw shield into the screen
        """
        if type == "yu_sh":
            for i in range(len(self.shields)):
                x = 866
                y = 14
                if self.shields.is_shield_exists(i):
                    card = CardView("yu_sh", i, self)
                    if not self.shields.is_shield_visible(i):
                        card.setPixmap(self.cardback_pixmap)
                    else:
                        card.set_card(self.shields[i])
                        pixmap = self.get_pixmap_card(self.shields[i].id)
                        card.setPixmap(pixmap)
                    card.setPos(x, y + i * 125)
                    self.view_scene.addItem(card)
                if not len(self.selected_card) == 0:
                    for sel_card in self.selected_card:
                        if sel_card[0] == type:
                            if sel_card[1] == i:
                                self.highlight_card(x, x + 85, y, y + 115, QColor(0, 0, 255))
                                break
        elif type == "op_sh":
            for i in range(len(self.opp_shields)):
                x = 74
                y = 139
                if self.opp_shields.is_shield_exists(i):
                    card = CardView("op_sh", i, self)
                    transform = QTransform().rotate(180)
                    pixmap = self.cardback_pixmap.transformed(transform)
                    card.setPixmap(pixmap)
                    card.setPos(x, y + i * 125)
                    self.view_scene.addItem(card)
                if not len(self.selected_card) == 0:
                    for sel_card in self.selected_card:
                        if sel_card[0] == type:
                            if sel_card[1] == i:
                                self.highlight_card(x, x + 85, y, y + 115, QColor(0, 0, 255))
                                break
                if self.select_mode == 21:
                    for pos in self.selected_shields:
                        if pos == i:
                            self.highlight_card(x, x + 85, y, y + 115, QColor(255, 0, 255))
                            break

    def add_bf_to_scene(self, type):
        """
        Draw card from battlefield into the screen
        """
        x = 232
        if type == "yu_bf":
            y = 389
            for i in range(len(self.bfield)):
                if self.bfield.is_taken(i):
                    card = CardView(type, i, self)
                    card.set_card(self.bfield[i])
                    pixmap = self.get_pixmap_card(self.bfield[i].id)
                    card.setPixmap(pixmap)
                    card.setPos(x + i * 95, y)
                    self.view_scene.addItem(card)
                if not len(self.selected_card) == 0:
                    for sel_card in self.selected_card:
                        if sel_card[0] == type:
                            if sel_card[1] == i:
                                # TODO: remove highlight when card was e.g. teleported to hand
                                self.highlight_card(x + i * 95, x + i * 95 + 85, y, y + 115, QColor(0, 0, 255))
                                break
        elif type == "op_bf":
            y = 264
            for i in range(len(self.opp_bfield)):
                if self.opp_bfield.is_taken(i):
                    card = CardView(type, i, self)
                    card.set_card(self.opp_bfield[i])
                    pixmap = self.get_pixmap_card(self.opp_bfield[i].id)
                    card.setPixmap(pixmap)
                    card.setPos(x + i * 95, y)
                    self.view_scene.addItem(card)
                if not len(self.selected_card) == 0:
                    for sel_card in self.selected_card:
                        if sel_card[0] == type:
                            if sel_card[1] == i:
                                # TODO: remove highlight when card was e.g. teleported to hand
                                self.highlight_card(x + i * 95, x + i * 95 + 85, y, y + 115, QColor(0, 0, 255))
                                break

    def add_sf_to_scene(self, type):
        """
        Draw card from battlefield into the screen
        """
        x = 707
        if type == "yu_sf":
            y = 389
            if self.sfield.is_taken():
                item = CardView(type, 0, self)
                card = self.sfield.get_card()
                item.set_card(card)
                pixmap = self.get_pixmap_card(card.id)
                item.setPixmap(pixmap)
                item.setPos(x, y)
                self.view_scene.addItem(item)
            if not len(self.selected_card) == 0:
                for sel_card in self.selected_card:
                    if sel_card[0] == type:
                        # TODO: remove highlight when card was e.g. teleported to hand
                        self.highlight_card(x, x + 85, y, y + 115, QColor(0, 0, 255))
        elif type == "op_sf":
            y = 264
            if self.opp_sfield.is_taken():
                item = CardView(type, 0, self)
                card = self.opp_sfield.get_card()
                item.set_card(card)
                pixmap = self.get_pixmap_card(card.id)
                item.setPixmap(pixmap)
                item.setPos(x, y)
                self.view_scene.addItem(item)
            if not len(self.selected_card) == 0:
                for sel_card in self.selected_card:
                    if sel_card[0] == type:
                        # TODO: remove highlight when card was e.g. teleported to hand
                        self.highlight_card(x, x + 85, y, y + 115, QColor(0, 0, 255))

    def add_graveyard_to_scene(self, type):
        if type == "yu_gv":
            x = 866
            y = 639
            if not self.graveyard.is_empty():
                item = CardView("yu_gv", 0, self)
                card = self.graveyard.get_last_card()
                item.set_card(card)
                item.setPixmap(self.get_pixmap_card(card.id))
                item.setPos(x, y)
                self.view_scene.addItem(item)
        elif type == "op_gv":
            x = 74
            y = 14
            if not self.opp_graveyard.is_empty():      
                item = CardView("op_gv", 0, self)
                card = self.opp_graveyard.get_last_card()
                item.set_card(card)
                transform = QTransform().rotate(180)
                item.setPixmap(self.get_pixmap_card(card.id).transformed(transform))
                item.setPos(x, y)
                self.view_scene.addItem(item)

    def add_log(self, msg, refresh=True):
        """Add log to log panel"""
        self.log_panel.append(msg)
        if refresh:
            self.refresh_screen()

    def send_message(self, *msg):
        if self.mode == 1:
            self.server.send_data(msg)
        else:
            self.client.send_data(msg)
        
    def turn_states(self, state): # TODO: change state to boolean, and name?
        """
        Set state of on start of your turn:
        0 -> first round of the game - don't draw a card
        1 -> every other round - draw a card
        """
        # TODO: unlock and untap all your mana and creatures
        if state == 1:
            self.mana.unlock_and_untap()
            self.bfield.reset_shield_count()
            self.card_to_draw = 1
            self.m_draw_a_card()
        self.card_to_mana = 1
        self.your_turn = 1

    def win(self):
        """Do someting when you win"""
        print("Winner!")

    def lose(self):
        """Do someting when you lose"""
        print("Loser!")

    def refresh_screen(self):
        """Refresh screen"""
        self.clear_view_scene()
        self.clear_preview_scene()
        self.draw_screen()

    def clear_view_scene(self):
        """Remove all items from view"""
        items = self.view_scene.items()
        for i in range(len(items)-1):
            self.view_scene.removeItem(items[i])

    def clear_preview_scene(self):
        """Remove all items from preview"""
        items = self.preview_scene.items()
        for i in range(len(items)-2):
            self.preview_scene.removeItem(items[i])

    def summon_effect(self, card):
        """Check and trigger the effects of played card"""
        print(f"Effects of card {card.name}: {str(card.effects)}")
        for effect in card.effects:
            if "teleport" in effect.keys():
                count = int(effect["teleport"]["count"])
                print(f"Teleport {count}")
                self.fun_queue.append((self.teleport, [True, count]))
            if "draw" in effect.keys():
                count = int(effect["draw"]["count"])
                print(f"Draw {count}")
                self.fun_queue.append((self.draw_cards, [count]))
            #if "destroy_blockers" in effect.keys():
            #    if effect["destroy_blockers"]["mode"] == "all":
            #        self.destroy_blocker(-1)
        if len(self.fun_queue) > 0:
            action, args = self.fun_queue.pop(0)
            action(*args)
        else:
            if self.your_turn == 5:
                if len(self.shields_to_destroy) == 0:
                    self.your_turn = 0
                    self.send_message(214)
                else:
                    self.add_log(f"You still have {len(self.shields_to_destroy)} shields to decide.")

    def can_attack_shield(self):
        if len(self.selected_card) == 0:
            return False
        pos = self.selected_card[0][1]
        if not self.bfield.is_tapped(pos) and self.bfield.get_shield_count(pos) > 0:
            return True
        return False

    def attack_creature(self, opp_pos):
        # TODO: check if it was card originaly selected, if yes, opponent didn't block (inform in log)
        your_card = self.bfield[self.selected_card[0][1]]
        opp_card = self.opp_bfield[opp_pos]
        your_power = int(your_card.power)
        for effect in your_card.effects:
            if "powerattacker" in effect.keys():
                your_power += int(effect["powerattacker"]["power"])
        if int(opp_card.power) < your_power:
            # Your creature wins
            self.m_move_to_graveyard("op_bf", opp_pos)
            destroyafterbattle = False
            for effect in your_card.effects:
                if "destroyafterbattle" in effect:
                    self.m_move_to_graveyard("yu_bf", self.selected_card[0][1])
                    self.add_log(f"Both creatures were destoyed due to battle results.")
                    destroyafterbattle = True
                    break
            if not destroyafterbattle:
                self.bfield.set_tapped(self.selected_card[0][1])
                self.add_log(f"Your creature {your_card.name} destroyed opponent {opp_card.name}")
        elif int(opp_card.power) == your_power:
            # Both are destroyed
            self.m_move_to_graveyard("yu_bf", self.selected_card[0][1])
            self.m_move_to_graveyard("op_bf", opp_pos)
            self.add_log(f"Both creatures were destoyed due to battle results.")
        else:
            # Your creature dies
            self.m_move_to_graveyard("yu_bf", self.selected_card[0][1])
            for effect in opp_card.effects:
                if "destroyafterbattle" in effect:
                    self.m_move_to_graveyard("op_bf", opp_pos)
            self.add_log(f"Your creature {your_card.name} was destoyed by opponent {opp_card.name} ")
        self.your_turn = 1
        self.select_mode = 0
        self.selected_card = []

    def creature_attacked(self, opp_pos, your_pos):
        # Opponent action - one of the creature is attacked
        # Check if you have blockers available
        blocker_available = False
        for creature in self.bfield:
            for effect in creature.effects:
                if "blocker" in effect:
                    if effect["blocker"]["mode"] == "all":
                        blocker_available = True

        if not blocker_available:
            # Proceed to attack
            self.send_message(112, your_pos)

        # Remember opponent choice
        self.chosen = your_pos

        # Decide what to do: block with blocker or pass blocking
        self.add_log("Choose either you block an attack with a blocker or allow it.")
        self.your_turn = 3 # special turn - block or pass - creature

    def shields_attacked(self, creature_pos, shields_pos):
        # Opponent action - one of the shield is attacked
        # Check if you have blockers available
        blocker_available = False
        for creature in self.bfield:
            for effect in creature.effects:
                if "blocker" in effect:
                    if effect["blocker"]["mode"] == "all":
                        blocker_available = True

        if not blocker_available:
            self.send_message(113)
        # TODO: log that your shield is attacked, you can either block attack with blocker or allow to attack
        self.add_log("You can choose either to block an attack with a blocker or allow it.")
        self.your_turn = 4 # special turn - block or pass - shield

    def attack_shield(self):
        self.send_message(14, *self.selected_shields)
        self.bfield.set_tapped(self.selected_card[0][1])
        self.selected_shields = []


    def shield_destroyed(self, idens):
        # Make all shields destroyed visible
        for iden in idens:
            self.shields.set_shield_visible(iden)
        self.shields_to_destroy = idens
        self.your_turn = 5
        self.add_log(f"{idens} shields were destroyed. Decide what to do with it.")

    def message_screen_request(self, bg_color, frame_color, text):
        """Message box for displaying important information. After one click it disappears."""
        # TODO: Debug why the box is not appearing
        bg = QGraphicsRectItem(100, 100, 200, 200)
        bg.setBrush(QBrush(bg_color))
        bg.setZValue(1.0)
        self.view_scene.addItem(bg)
        frame = QGraphicsRectItem(99, 99, 202, 202)
        frame.setPen(QPen(frame_color))
        frame.setZValue(2.0)
        self.view_scene.addItem(frame)
        text = QGraphicsTextItem(text)
        text.setPos(110, 110)
        text.setZValue(3.0)
        self.view_scene.addItem(text)
        self.focus_request = True
        self.select_mode = 1

    #  EFFECT METHODS
    #####################################################

    def post_effect(self):
        # If it was effect from the spell
        if self.spell_played:
            self.spell_played = False
            card = self.sfield.remove_card()
            self.graveyard.add_card(card)
            self.refresh_screen()
        if len(self.fun_queue) > 0:
            # functions still in the queue, run them
            action, args = self.fun_queue.pop(0)
            action(*args)
        else:
            # If card was from shield, check if all shields were handled
            if self.your_turn == 5 and len(self.shields_to_destroy) == 0:
                self.your_turn = 0
                self.send_message(214)

    def teleport(self, firsttime, count=0):
        if firsttime:
            self.add_log(f"Choose {count} cards in the battlefield to activate the effect.")
            self.card_to_choose = count
            self.type_to_choose = ["yu_bf", "op_bf"]
            self.selected_card = []
            self.fun_queue.insert(0, (self.teleport, [False]))
            print(self.fun_queue)
        else:
            print(self.selected_card)
            for card in self.selected_card:
                self.m_return_card_to_hand(card[0], card[1])
            self.selected_card = []
            self.type_to_choose = []
            self.select_mode = 0
            self.refresh_screen()
            self.post_effect()

    def draw_cards(self, count):
        self.card_to_draw += count
        while self.card_to_draw > 0:
            self.m_draw_a_card()
        self.post_effect()

    #   MENU METHODS
    #####################################################

    def m_draw_a_card(self):
        """Draw a top card from your deck and add it to your hand"""
        # Check if you are allowed to draw a card
        if self.card_to_draw == 0:
            return
        if not len(self.deck) == 0:
            card_id = self.deck.pop(0)
            card = self.database.get_card(card_id)
            self.add_log("You draw a card {}.".format(card.name))
            self.hand.add_card(card)
            self.send_message(3)
        else:
            self.add_log("You don't have enough cards to draw from. You lose!")
            self.lose()
        self.card_to_draw -= 1
        self.refresh_screen()

    def m_end_turn(self):
        # TODO: in the future, ask if you really want to end the turn when none action were taken
        # end your turn
        self.add_log("End of your turn.")
        self.send_message(2)
        self.selected_card = []
        self.your_turn = 0

    def m_accept_cards(self):
        print(self.fun_queue)
        action, args = self.fun_queue.pop(0)
        print(action, args)
        action(args)
        if self.spell_played:
            # Move spell to graveyard after usage
            self.m_move_to_graveyard("yu_sf", 0)
            self.spell_played = False
        
    def m_summon_card(self, iden):
        card = self.hand[iden]
        if self.mana.can_be_played(card):
            # TODO: check if card can be played due to effect (e.g. not enough opponent's cards)
            if card.card_type == "Creature":
                # TODO: check if creature can be summoned (not full board)

                card = self.hand.remove_card(iden)
                pos = self.bfield.add_card(card)
                self.mana.lock_used_mana()
                self.log.info(f"You've played a creature {card.name}")
                self.add_log(f"You have played {card.name} on position {pos}")
                self.send_message(4, card.id, pos)
                self.summon_effect(card)
            elif card.card_type == "Spell":
                # Spells are played on 6th space, separate of creature ones
                if not self.sfield.is_taken():
                    card = self.hand.remove_card(iden)
                    self.sfield.set_card(card)
                    self.mana.lock_used_mana()
                    self.log.info(f"You've played a spell {card.name}")
                    self.add_log(f"You have played spell {card.name}")
                    self.send_message(4, card.id, 5)
                    self.spell_played = True
                    self.summon_effect(card)
        else:
            # Not enough mana tapped, do nothing
            return
        self.refresh_screen()

    def m_choose_card(self, set, iden):
        # Action: Choose a card as a target for e.g. effect, attack
        if [set, iden] in self.selected_card:
            # can't choose the same card twice
            return
        # TODO: if not effect or spell targeting, if selected_card is creature set to him shield count
        self.selected_card.append([set, iden])
        if set == 'yu_bf':
            if "shieldbreaker" in self.bfield[iden].effects:
                count = int(self.bfield[iden].effects["shieldbreaker"]["count"])
            else:
                count = 1
            self.bfield.set_shield_count(iden, count)
        self.refresh_screen()

    def m_unchoose_card(self, set, iden):
        self.selected_card.remove((set, iden))
        self.refresh_screen()
        
    def m_return_card_to_hand(self, set, iden):
        # Action: Return a card to hand 
        if set == "yu_bf":
            card = self.bfield.remove_card(iden)
            self.hand.add_card(card)
            self.send_message(5, 1, 1, iden)
        elif set == "yu_mn":
            card = self.mana.remove_card(iden)
            self.hand.add_card(card)
            self.send_message(5, 1, 0, iden)
        elif set == "op_mn":
            self.opp_mana.remove_card(iden)
            self.send_message(5, 0, 0, iden)
            self.opp_hand.add_placeholder()
        elif set == "op_bf":
            self.opp_bfield.remove_card(iden)
            self.send_message(5, 0, 1, iden)
            self.opp_hand.add_placeholder()
        self.refresh_screen()
        
    def m_return_shield_to_hand(self, iden):
        # Action: Return your card under destroyed shield to hand
        card = self.shields.remove_shield(iden)
        self.hand.add_card(card)
        self.send_message(114, iden)
        self.shields_to_destroy.remove(iden)
        if len(self.shields_to_destroy) == 0:
            self.your_turn = 0
            self.send_message(214)
        else:
            self.add_log(f"You still have {len(self.shields_to_destroy)} shields to decide.")
        self.refresh_screen()

    def m_play_destroyed_shield(self, set, iden):
        # Action: Play a shield with shield trigger
        self.shields_to_destroy.remove(iden)
        card = self.shields.remove_shield(iden)
        if self.cardlist[card].card_type == 'Spell':
            self.sfield.set_card(card)
            self.send_message(4, card.id, 5)
            self.spell_played = True
            self.summon_effect(card)
        elif self.cardlist[card].card_type == 'Creature':
            # Handled in menu if there is space left
            pos = self.bfield.add_card(card)
            self.send_message(4, card.id, pos)
            self.summon_effect(card)
        self.refresh_screen()

    def m_move_to_graveyard(self, set, iden):
        # Action: Move a card to the graveyard
        if set == "yu_bf":
            card = self.bfield.remove_card(iden)
            self.graveyard.add_card(card)
            self.send_message(6, 1, 1, iden)
        elif set == "yu_sf":
            card = self.sfield.remove_card()
            self.graveyard.add_card(card)
            self.send_message(6, 1, 1, 5)
        elif set == "yu_mn":
            card = self.mana.remove_card(iden)
            self.graveyard.add_card(card)
            self.send_message(6, 1, 0, iden)
        elif set == "op_mn":
            card = self.opp_mana.remove_card(iden)
            self.opp_graveyard.add_card(card)
            self.send_message(6, 0, 0, iden)
        elif set == "op_bf":
            card = self.opp_bfield.remove_card(iden)
            self.opp_graveyard.add_card(card)
            self.send_message(6, 0, 1, iden)
        elif set == "op_sf":
            card = self.opp_sfield.remove_card()
            self.opp_graveyard.add_card(card)
            self.send_message(6, 0, 1, 5)
        self.refresh_screen()
        
    def m_add_to_mana(self, iden):
        if self.card_to_mana > 0:
            card = self.hand.remove_card(iden)
            self.mana.add_card(card)
            self.card_to_mana -= 1
            self.send_message(7, card.id)
            self.refresh_screen()
        
    def m_add_to_shield(self, iden):
        card = self.hand.remove_card(iden)
        pos = self.shields.add_shield(card)
        self.send_message(8, pos)
        self.refresh_screen()
        
    def m_tap_mana(self, set, iden):
        if not self.mana.is_tapped(iden):
            self.mana.tap_card(iden)
            self.send_message(9, 1, iden)
        self.refresh_screen()
        
    def m_untap_mana(self, set, iden):
        if self.mana.is_tapped(iden):
            self.mana.untap_card(iden)
            self.send_message(9, 0, iden)
        self.refresh_screen()
        
    def m_look_at_shield(self, iden):
        self.shields.set_shield_visible(iden)
        self.send_message(10, iden)
        self.refresh_screen()

    def m_put_shield(self, iden):
        # TODO: implement this as action on the end of turn if shield was revealed
        # self.shields[iden-1][1] = True
        self.refresh_screen()
        
    def m_select_creature(self, set, iden):
        # Action: select your creature to attack another creature or shield
        # TODO: check if creature can attack (ability, tapped)
        if self.bfield.is_tapped(iden):
            return
        self.selected_card = [(set, iden)]
        self.select_mode = 2

    def m_unselect_creature(self, set, iden):
        # Action: unselect your creature to attack another creature or shield
        self.selected_card.remove((set, iden))
        self.select_mode = 0

    def m_attack_creature(self, set, iden):
        # Action: attack creature with your creature
        if len(self.selected_card) == 0 or not self.select_mode == 2: 
            # None of the attacking creatures is selected
            return
        if not self.opp_bfield.is_tapped(iden) and True: # TODO: check if your card has ability to attack untapped cards
            return
        self.add_log(f"Attacking card {self.opp_bfield[iden].name} with card {self.bfield[self.selected_card[0][1]].name}")
        self.send_message(12, self.selected_card[0][1], iden) # Inform opponent about the attack
        self.your_turn = 0

    def m_select_shield_to_attack(self, iden):
        if iden in self.selected_shields:
            return
        self.selected_shields.append(iden)
        self.select_mode = 21

    def m_remove_shield_to_attack(self, iden):
        self.selected_shields.remove(iden)

    def m_shield_attack(self):
        if len(self.selected_card) == 0 or not self.select_mode == 21:
            return
        self.send_message(13, self.selected_card[0][1], *self.selected_shields)
        self.select_mode = 0
        self.your_turn = 0

    def m_block_with_creature(self, set, iden):
        self.add_log(f"Blocking attack with {iden}")
        self.your_turn = 0
        self.send_message(112, iden)

    def m_pass_attack(self): 
        self.add_log(f"Passing blocking")
        self.your_turn = 0
        self.send_message(112, self.chosen)

    def m_shield_block_with_creature(self, set, iden):
        self.add_log(f"Blocking attack with {iden}")
        self.your_turn = 0
        self.send_message(113, iden)

    def m_shield_pass_attack(self): 
        self.add_log(f"Passing blocking")
        self.your_turn = 0
        self.send_message(113)  
   
    def m_opp_look_at_hand(self, iden):
        self.send_message(11, 0, iden)
        
    def m_opp_look_at_shield(self, iden):
        self.send_message(11, 1, iden)
        
    def m_look_graveyard(self, set):
        if set == "op_gv":
            graveyard_look = GraveyardView(self.opp_graveyard, self)
        elif set == "yu_gv":
            graveyard_look = GraveyardView(self.graveyard, self)
        else:
            return
        graveyard_look.show()
