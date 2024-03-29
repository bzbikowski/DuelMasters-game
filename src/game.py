import logging
import random

from PySide6.QtCore import Qt, QTimer, QThread, Slot, Signal, QRectF
from PySide6.QtGui import QBrush, QColor, QPen, QPixmap, QTransform, QImage, QFont
from PySide6.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, \
    QTextEdit, QLabel, QPushButton, QGraphicsRectItem, QGraphicsTextItem, QMessageBox
from src.ui.ui_game import Ui_Game
from src.sidelogger import SideLogger
from src.network.client import Client
from src.network.server import Server
from src.views import GameView, CardView
from src.views.common.commonwindow import CommonWindow
from src.views.graveyard import GraveyardWindow
from src.dialogs import ServerDialog, ClientDialog
from src.controller import Controller
from src.zones import Battlezone, Graveyardzone, Handzone, Manazone, Shieldzone, Spellzone
from src.enums import SetName, EffectName


class Game(QWidget):
    """
    Main class in application.
    """
    def __init__(self, mode, deck, database, debug, parent=None):
        super(Game, self).__init__()
        self.ui = Ui_Game()
        self.ui.setupUi(self)
        self.log = logging.getLogger("game")
        self.mode = mode
        self.database = database
        # self.move((screen_width - self.width)/2, (screen_height - self.height)/2 - 20)
        self.debug_mode = debug
        self.parent = parent
        self.deck = deck

        # Game variables
        self.locked = False
        self.isServer = False
        self.started = False
        self.first = False  # who has the first move in the game
        self.card_to_draw = 0
        self.card_to_mana = 0

        ## Your turn info:
        # 0 - not your turn
        # 1 - your turn
        # 2 - special turn
        # 3 - block or pass creature
        # 4 - block or pass shield
        # 5 - shield destroyed
        self.your_turn = 0
        self.selected_card = None
        self.focus_request = False

        ## Select mode info:
        # 0 - no select mode
        # 1 - effects
        # 2 - creature
        # 21 - shields attack
        self.select_mode = 0
        self.selected_card_choose = 0
        self.selected_card_targets = []
        self.turn_count = 1 # start from 1
        self.spell_played = None

        # Setup scenes
        self.view_scene = GameView(self)
        self.ui.view.setScene(self.view_scene)
        self.view_scene.setBackgroundBrush(QBrush(QColor(0, 0, 0)))

        self.preview_scene = QGraphicsScene()
        self.ui.preview.setScene(self.preview_scene)
        self.preview_scene.setBackgroundBrush(QBrush(QColor(0, 0, 0)))

        # Setup logging on the screen
        self.log_panel = SideLogger()

        self.controller = Controller(self)

        # Run application in specific mode
        if self.mode == 1:
            self.wait_for_connection()
        else:
            self.connect_to_room()

    ## Getters
    #######################
    def get_your_turn(self):
        return self.your_turn

    def get_select_mode(self):
        return self.select_mode

    def get_spell_played(self):
        return self.spell_played
    
    def get_selected_card(self):
        return self.selected_card

    def get_selected_shields(self):
        return self.selected_shields

    def get_selected_card_choose(self):
        return self.selected_card_choose

    def get_selected_card_targets(self):
        return self.selected_card_targets

    def get_your_bf(self):
        return [card for card in self.bfield]

    def get_your_mn(self):
        return [card for card in self.mana]

    ## Internal functions
    #######################
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
        self.log.debug("GAME - DISCONNECTED")
        self.close()

    def handle_error(self):
        self.log.info("There was a problem with connectivity to other player. Please try again later.")
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
        self.client.errorOccurred.connect(self.handle_error)
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

        ip_port = self.server.port

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
        self.init_game()
        self.add_turn_info(False) # draw_screen is called after, so do not refresh
        if self.mode == 1:
            if random.random() < 0.5:
                self.send_message(0)
                self.add_log("You start the game! Your turn.", False) # draw_screen is called after, so do not refresh
                self.first = True
                self.new_round(False)
                self.log.info(f"Turn {self.turn_count}: Host turn.")
            else:
                self.send_message(1)
                self.add_log("Opponent starts the game.", False) # draw_screen is called after, so do not refresh
                self.log.info(f"Turn {self.turn_count}: Opponent turn.")
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
        # display logs
        x_pos = 20
        y_pos = 748
        x_width = 296
        for i in range(len(self.log_panel)):
            log, id = self.log_panel[i]

            text = QGraphicsTextItem(log)
            text.setTextWidth(x_width - 10)
            text_height = text.boundingRect().height()
            y_pos -= text_height + 10

            text.setPos(x_pos + 5, y_pos + 3)
            frame = QGraphicsRectItem(x_pos, y_pos, x_width, text_height)
            if id == 0: # Log message
                frame.setBrush(QBrush(QColor(0, 0, 0, 100)))
            elif id == 1: # Turn info
                frame.setBrush(QBrush(QColor(127, 127, 127, 100)))

            self.preview_scene.addItem(frame)
            self.preview_scene.addItem(text)

            if y_pos < 0: # TODO: make it scrollable and remove this block
                break

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
        if c_id is not None:
            self.draw_preview_card(c_id)
        self.highlight_card(x, x + 85, y, y + 115, QColor(255, 0, 0))

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
        # add black background window
        frame = QGraphicsRectItem(0, 0, 336, 453)
        frame.setBrush(QBrush(QColor(0, 0, 0)))
        self.preview_scene.addItem(frame)

        # add preview of the card
        pixmap = self.get_pixmap_card(card_id, 'medium_res') 
        card_prev = QGraphicsPixmapItem(pixmap)
        card_prev.setPos(8, 0)
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
                                self.highlight_card(x, x + 85, y + i * 125, y + i * 125 + 115, QColor(0, 0, 255))
                                break
                if self.select_mode == 21:
                    for pos in self.selected_shields:
                        if pos == i:
                            self.highlight_card(x, x + 85, y + i * 125, y + i * 125 + 115, QColor(255, 0, 255))
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
                    if self.bfield.is_tapped(i):
                        image = pixmap.toImage()
                        image = image.convertToFormat(QImage.Format_Grayscale8)
                        pixmap = pixmap.fromImage(image)
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
                    if self.opp_bfield.is_tapped(i) or self.opp_bfield.has_effect("treatastapped", i):
                        image = pixmap.toImage()
                        image = image.convertToFormat(QImage.Format_Grayscale8)
                        pixmap = pixmap.fromImage(image)
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

    def message_screen_request(self, bg_color, frame_color, text):
        """Message box for displaying important information. After one click it disappears."""
        # TODO: currently this box disappears after refresh_screen function, find better solution
        bg = QGraphicsRectItem(100, 100, 200, 200) # TODO: center it
        bg.setBrush(QBrush(bg_color))
        bg.setZValue(1.0)
        self.view_scene.addItem(bg)
        frame = QGraphicsRectItem(99, 99, 202, 202) # TODO: center it
        frame.setPen(QPen(frame_color))
        frame.setZValue(2.0)
        self.view_scene.addItem(frame)
        text = QGraphicsTextItem(text)
        text.setPos(110, 110) # TODO: center it
        text.setZValue(3.0)
        self.view_scene.addItem(text)
        self.focus_request = True
        self.select_mode = 1

    def add_log(self, msg, refresh=True):
        """Add log to log panel"""
        self.log_panel.append(msg)
        if refresh:
            self.refresh_screen()

    def add_turn_info(self, refresh=True):
        """Add log to log panel"""
        self.log_panel.print_turn(self.turn_count)
        if refresh:
            self.refresh_screen()

    def send_message(self, *msg):
        if self.mode == 1:
            self.server.send_data(msg)
        else:
            self.client.send_data(msg)
        
    def new_round(self, not_first=True):
        """
        Set state of on start of your turn:
        0 -> first round of the game - don't draw a card
        1 -> every other round - draw a card
        """
        if not_first:
            if self.first: # your turns are the start for synced turns
                self.turn_count += 1
                self.send_message(27)
                self.add_turn_info()
            self.mana.unlock_and_untap()
            self.bfield.reset_board()
            for pos, _ in self.bfield.get_creatures_with_pos():
                self.send_message(16, 1, 1, pos)
            self.card_to_draw = 1
            self.a_draw_card()
        self.card_to_mana = 1
        self.your_turn = 1
        self.blocker_list = []

    def win(self, from_opp=False):
        """You won the game"""
        # TODO: victory screen
        if not from_opp:
            self.send_message(25)
        _ = QMessageBox.information(self, "Information", "You won the game! Press ok to return to main menu.",
                                             QMessageBox.Ok, QMessageBox.NoButton)
        self.close()

    def lose(self, from_opp=False):
        """You lost the game"""
        # TODO: loser screen
        if not from_opp:
            self.send_message(26)
        _ = QMessageBox.information(self, "Information", "You lost the game! Press ok to return to main menu.",
                                             QMessageBox.Ok, QMessageBox.NoButton)
        self.close()
        
    def can_attack_shield(self):
        """Check if selected creature can attack shield"""
        if len(self.selected_card) == 0:
            return False
        can_attack = True
        pos = self.selected_card[0][1]
        for effect in self.bfield[pos].effects:
            if "notattacking" in effect:
                if effect["notattacking"]["mode"] in ["all", "player"]:
                    can_attack = False
                    break
        if self.bfield.is_tapped(pos) or self.bfield.get_shield_count(pos) <= len(self.selected_shields):
            can_attack = False
        return can_attack

    def pop_fun_queue(self, index):
        """Pop and return item from the effects queue"""
        return self.fun_queue.pop(index)

    def attack_creature(self, opp_pos):
        """Attack your opponent creature with selected card"""
        # TODO: check if it was card originaly selected, if yes, opponent didn't block (inform in log)
        your_card = self.bfield[self.selected_card[0][1]]
        opp_card = self.opp_bfield[opp_pos]
        your_power = int(your_card.power)
        for effect in your_card.effects:
            if "powerattacker" in effect:
                if effect["powerattacker"]["mode"] == "power":
                    your_power += int(effect["powerattacker"]["power"])
                elif effect["powerattacker"]["mode"] == "race":
                    # Check if there are any creatures with that race on your bfield
                    for creature in self.bfield:
                        if creature.race == effect["powerattacker"]["race"]:
                            your_power += int(effect["powerattacker"]["power"])
                            try:
                                effect["powerattacker"]["each"]
                            except KeyError:
                                break
                elif effect["powerattacker"]["mode"] == "graveyard":
                    # Check if there are any creatures with that civ in your graveyard
                    for card in self.graveyard:
                        if card.civ == effect["powerattacker"]["civ"]:
                            your_power += int(effect["powerattacker"]["power"])
                            try:
                                effect["powerattacker"]["each"]
                            except KeyError:
                                break

        if int(opp_card.power) < your_power:
            # Your creature wins
            is_opp_card_slayer = self.opp_bfield.has_effect("slayer", opp_pos)
            self.a_move_to_graveyard("op_bf", opp_pos)
            destroyafterbattle = False
            for effect in your_card.effects:
                if "destroyafterbattle" in effect:
                    destroyafterbattle = True
                    break
            if destroyafterbattle or is_opp_card_slayer:
                self.a_move_to_graveyard("yu_bf", self.selected_card[0][1])
                self.add_log(f"Both creatures were destoyed due to battle results.")
            else:
                self.bfield.set_tapped(self.selected_card[0][1])
                self.send_message(16, 0, 1, self.selected_card[0][1])
                self.add_log(f"Your creature {your_card.name} destroyed opponent {opp_card.name}")
        elif int(opp_card.power) == your_power:
            # Both are destroyed
            self.a_move_to_graveyard("yu_bf", self.selected_card[0][1])
            self.a_move_to_graveyard("op_bf", opp_pos)
            self.add_log(f"Both creatures were destoyed due to battle results.")
        else:
            # Your creature dies
            is_your_card_slayer = self.bfield.has_effect("slayer", self.selected_card[0][1])
            self.a_move_to_graveyard("yu_bf", self.selected_card[0][1])
            destroyafterbattle = False
            for effect in opp_card.effects:
                if "destroyafterbattle" in effect:
                    destroyafterbattle = True
                    break
            if destroyafterbattle or is_your_card_slayer:
                self.a_move_to_graveyard("op_bf", opp_pos)
                self.add_log(f"Both creatures were destoyed due to battle results.")
            else:
                self.add_log(f"Your creature {your_card.name} was destoyed by opponent {opp_card.name} ")
        self.your_turn = 1
        self.select_mode = 0
        self.selected_card = []

    def creature_attacked(self, opp_pos, your_pos):
        """One of the creature is attacked"""
        # Check if you have blockers available
        blocker_list = self.bfield.get_available_blockers()

        pass_blockers = False
        for effect in self.opp_bfield[opp_pos].effects:
            if "passblockers" in effect:
                mode = effect["passblockers"]["mode"]
                if mode == "all":
                    pass_blockers = True
                    break
                elif mode == "creature":
                    count = int(effect["passblockers"]["count"])
                    if len(self.opp_bfield) >= count + 1:
                        pass_blockers = True
                        break
                elif mode == "power":
                    power = int(effect["passblockers"]["power"])
                    blocked_by = []
                    for blocker_pos in blocker_list:
                        if self.bfield[blocker_pos].power > power:
                            blocked_by.append(blocker_pos)
                    if len(blocked_by) > 0:
                        blocker_list = blocked_by
                    else:
                        pass_blockers = True

        if pass_blockers or len(blocker_list) == 0:
            # Proceed to attack
            self.send_message(112, your_pos)
        else:
            # Remember opponent choice and available blocker list
            self.chosen = your_pos
            self.blocker_list = blocker_list

            # Decide what to do: block with blocker or pass blocking
            self.add_log("Choose either you block an attack with a blocker or allow it.")
            self.your_turn = 3 # special turn - block or pass - creature

    def shields_attacked(self, opp_pos, shields_pos):
        """One of the shield is attacked"""
        # Check if you have blockers available
        blocker_list = self.bfield.get_available_blockers()

        pass_blockers = False
        for effect in self.opp_bfield[opp_pos].effects:
            if "passblockers" in effect:
                mode = effect["passblockers"]["mode"]
                if mode == "all":
                    pass_blockers = True
                    break
                elif mode == "creature":
                    count = int(effect["passblockers"]["count"])
                    if len(self.opp_bfield) >= count + 1:
                        pass_blockers = True
                        break
                elif mode == "power":
                    power = int(effect["passblockers"]["power"])
                    blocked_by = []
                    for blocker_pos in blocker_list:
                        if self.bfield[blocker_pos].power > power:
                            blocked_by.append(blocker_pos)
                    if len(blocked_by) > 0:
                        blocker_list = blocked_by
                    else:
                        pass_blockers = True

        if pass_blockers or len(blocker_list) == 0:
            self.send_message(113)
        else:
            self.blocker_list = blocker_list

            self.add_log("You can choose either to block an attack with a blocker or allow it.")
            self.your_turn = 4 # special turn - block or pass - shield

    def attack_shield(self):
        """Send information to opponent that you destroyed his shields"""
        self.send_message(14, *self.selected_shields)
        self.bfield.set_tapped(self.selected_card[0][1])
        self.send_message(16, 0, 1, self.selected_card[0][1])
        self.selected_shields = []

    def shield_destroyed(self, idens):
        """Your shields were destroyed."""
        # Make all shields destroyed visible
        for iden in idens:
            self.shields.set_shield_visible(iden)
        self.shields_to_destroy = idens
        self.your_turn = 5
        self.add_log(f"{idens} shields were destroyed. Decide what to do with it.")
        
    def directly_attacked(self, opp_pos):
        """You are directly attacked by opponent card"""
        # Check if you have blockers available
        blocker_list = self.bfield.get_available_blockers()

        pass_blockers = False
        for effect in self.opp_bfield[opp_pos].effects:
            if "passblockers" in effect:
                mode = effect["passblockers"]["mode"]
                if mode == "all":
                    pass_blockers = True
                    break
                elif mode == "creature":
                    count = int(effect["passblockers"]["count"])
                    if len(self.opp_bfield) >= count + 1:
                        pass_blockers = True
                        break
                elif mode == "power":
                    power = int(effect["passblockers"]["power"])
                    blocked_by = []
                    for blocker_pos in blocker_list:
                        if self.bfield[blocker_pos].power > power:
                            blocked_by.append(blocker_pos)
                    if len(blocked_by) > 0:
                        blocker_list = blocked_by
                    else:
                        pass_blockers = True

        if pass_blockers or len(blocker_list) == 0:
            self.send_message(124)
        else:
            self.blocker_list = blocker_list

            self.add_log("You can choose either to block an attack with a blocker or allow it.")
            self.your_turn = 6 # special turn - block or pass - direct

    def summon_effect(self, card):
        """Check and trigger the effects of played card"""
        for effect in card.effects:
            if "teleport" in effect.keys():
                mode = effect["teleport"]["mode"]
                if mode == "count":
                    count = int(effect["teleport"]["count"])
                    self.fun_queue.append((self.teleport, [True, mode, count]))
                elif mode == "power":
                    power = int(effect["teleport"]["power"])
                    self.fun_queue.append((self.teleport, [True, mode, power]))
            if "draw" in effect.keys():
                mode = effect["draw"]["mode"]
                try:
                    race =  effect["draw"]["race"]
                except KeyError:
                    race = None
                count = int(effect["draw"]["count"])
                self.fun_queue.append((self.draw_cards, [mode, count, race]))
            if "destroyblockers" in effect.keys():
                self.fun_queue.append((self.destroy_all_blockers, []))
            if "returngraveyard" in effect.keys():
                mode = effect["returngraveyard"]["mode"]
                count = int(effect["returngraveyard"]["count"])
                self.fun_queue.append((self.return_from_graveyard, [mode, count]))
            if "findcard" in effect.keys():
                mode = effect["findcard"]["mode"]
                type = effect["findcard"]["type"]
                if type == "all":
                    type = ["creature", "spell"]
                count =  int(effect["findcard"]["count"])
                self.fun_queue.append((self.search_for_card, [mode, type, count]))
            if "destroycreatures" in effect.keys():
                mode = effect["destroycreatures"]["mode"]
                try:
                    count =  int(effect["destroycreatures"]["count"])
                except KeyError:
                    count = None
                try:
                    power =  int(effect["destroycreatures"]["power"])
                except KeyError:
                    power = None
                try:
                    opp_choice = effect["destroycreatures"]["opponentchoose"]
                except KeyError:
                    opp_choice = None
                self.fun_queue.append((self.destroy_creature, [mode, count, power, opp_choice]))
            if "puttomana" in effect.keys():
                mode = effect["puttomana"]["mode"]
                count =  int(effect["puttomana"]["count"])
                args = [(key, value) for key, value in effect["puttomana"].items() if key not in ["mode", "count"]]
                self.fun_queue.append((self.put_card_to_mana, [mode, count, *args]))
            if "tap" in effect.keys():
                mode = effect["tap"]["mode"]
                if mode == "count":
                    count =  int(effect["tap"]["count"])
                    self.fun_queue.append((self.tap_creature, [mode, count]))
                else:
                    self.fun_queue.append((self.tap_creature, [mode]))
            if "oneforone" in effect.keys():
                count =  int(effect["oneforone"]["count"])
                self.fun_queue.append((self.one_for_one, [count]))
            if "discard" in effect.keys():
                count = int(effect["discard"]["count"])
                self.fun_queue.append((self.discard_cards, [count]))
            if "sacrifice" in effect.keys():
                count =  int(effect["sacrifice"]["count"])
                self.fun_queue.append((self.sacrifice_creature, [count]))
            if "manasacrifice" in effect.keys():
                count =  int(effect["manasacrifice"]["count"])
                self.fun_queue.append((self.sacrifice_mana, [count]))
            if "treatastapped" in effect.keys():
                count =  int(effect["treatastapped"]["count"])
                self.fun_queue.append((self.treat_card_as_tapped, [count]))
            if "give" in effect.keys():
                mode = effect["give"]["mode"]
                count = int(effect["give"]["count"])
                effect = effect["give"]["effect"]
                self.fun_queue.append((self.give_effect, [mode, count, effect]))

        if len(self.fun_queue) > 0:
            action, args = self.fun_queue.pop(0)
            action(*args)
        else:
            if self.your_turn == 5:
                if len(self.shields_to_destroy) == 0:
                    self.your_turn = 0
                    self.send_message(314)
                else:
                    self.add_log(f"You still have {len(self.shields_to_destroy)} shields to decide.")

    ####################
    #  EFFECT METHODS  #
    ####################
    def post_effect(self):
        """Run after every effect function"""
        if len(self.fun_queue) > 0:
            # functions still in the queue, run them
            action, args = self.fun_queue.pop(0)
            action(*args)
        else:
            # If it was effect from the spell, move card to the graveyard
            if self.spell_played:
                self.spell_played = False
                self.a_move_to_graveyard("yu_sf", 0)
                self.refresh_screen()
            # If card was from shield, check if all shields were handled
            if self.your_turn == 5 and len(self.shields_to_destroy) == 0:
                self.your_turn = 0
                self.send_message(314)

    def teleport(self, firsttime, mode, *args):
        if firsttime:
            if mode=="count":
                count = args[0]
                self.add_log(f"Choose {count} cards in the battlefield to activate the effect.")
                self.selected_card_choose = count
                self.selected_card_targets = [("yu_bf", ["*"]), ("op_bf", ["*"])]
                self.selected_card = []
                self.fun_queue.insert(0, (self.teleport, [False, mode]))
                self.select_mode = 1
            elif mode=="power":
                power = args[0]
                self.add_log(f"All cards with power equal or less than {power} are returned to hand.")
                for pos, card in self.bfield.get_creatures_with_pos():
                    if card.power <= power:
                        self.a_return_card_to_hand("yu_bf", pos)
                for pos, card in self.opp_bfield.get_creatures_with_pos():
                    if card.power <= power:
                        self.a_return_card_to_hand("op_bf", pos)
                self.post_effect()
        else:
            for card in self.selected_card:
                self.a_return_card_to_hand(card[0], card[1])
            self.selected_card = []
            self.selected_card_targets = []
            self.select_mode = 0
            self.refresh_screen()
            self.post_effect()

    def draw_cards(self, mode, *args):
        if mode == "count":
            count = args[0]
            self.card_to_draw += count
            while self.card_to_draw > 0:
                self.a_draw_card()
        elif mode == "race":
            count = args[0]
            race = args[1]
            creature_exists = False
            for card in self.bfield:
                if card.race == race:
                    creature_exists = True
                    break
            if creature_exists:
                self.card_to_draw += count
                while self.card_to_draw > 0:
                    self.a_draw_card()
        self.post_effect()

    def destroy_all_blockers(self):
        # Your blockers
        for creature_pos, creature_card in self.bfield.get_creatures_with_pos():
            for effect in creature_card.effects:
                if "blocker" in effect:
                    self.a_move_to_graveyard("yu_bf", creature_pos)
        # Opponent blockers
        for creature_pos, creature_card in self.opp_bfield.get_creatures_with_pos():
            for effect in creature_card.effects:
                if "blocker" in effect:
                    self.a_move_to_graveyard("op_bf", creature_pos)
        self.post_effect()

    def return_from_graveyard(self, mode, count):
        # TODO: add typing, assume creatures for now
        if mode == "hand":
            cards = [card.id for card in self.graveyard if str.lower(card.card_type) == "creature"]
            settings = {"cards": cards, "count": count}
            self.cards_window = CommonWindow(settings, self)
            self.cards_window.card_choosed.connect(self.post_return_from_graveyard)
            self.cards_window.show()

    def post_return_from_graveyard(self):
        # TODO: better doc
        for card_id in self.cards_window.get_selected_items():
            card = self.database.get_card(card_id)
            self.graveyard.remove_card(card)
            self.add_log(f"Added card {card.name} from graveyard to hand")
            self.send_message(19, card_id)
            self.hand.add_card(card)
        self.refresh_screen()
        self.post_effect()

    def search_for_card(self, mode, type, count):
        # TODO: better doc
        cards = []
        if mode == "deck":
            # TODO: cache results? make it faster?
            cards = [iden for iden in self.deck if str.lower(self.database.get_card(iden).card_type) in type]
            settings = {"cards": cards, "count": count}
            self.cards_window = CommonWindow(settings, self)
            self.cards_window.card_choosed.connect(self.post_search_for_card)
            self.cards_window.show()

    def post_search_for_card(self):
        # TODO: better doc
        for card_id in self.cards_window.get_selected_items():
            card = self.database.get_card(card_id)
            self.deck.remove(card_id)
            self.add_log(f"Added card {card.name} from deck to hand")
            self.send_message(18, card_id)
            self.hand.add_card(card)
        random.shuffle(self.deck)
        self.refresh_screen()
        self.post_effect()

    def destroy_creature(self, mode, count, power, opp_choice):
        # TODO: better doc
        valid_targets = {"op_bf": [], "yu_bf": []}

        if mode == "untapped":
            # Untappped opponent cards
            for pos, _ in self.opp_bfield.get_creatures_with_pos():
                if not self.opp_bfield.is_tapped(pos):
                    valid_targets["op_bf"].append(pos)
        elif mode == "all":
            # All creatures cards on battlefields
            for pos, _ in self.bfield.get_creatures_with_pos():
                valid_targets["yu_bf"].append(pos)
            for pos, _ in self.opp_bfield.get_creatures_with_pos():
                valid_targets["op_bf"].append(pos)
        elif mode == "opponent":
            # All opponent creatures
            for pos, _ in self.opp_bfield.get_creatures_with_pos():
                valid_targets["op_bf"].append(pos)

        if count == None:
            # Destroy cards based on power
            if power == None:
                # Destroy all cards
                for pos in valid_targets["yu_bf"]:
                    self.a_move_to_graveyard("yu_bf", pos)
                for pos in valid_targets["op_bf"]:
                    self.a_move_to_graveyard("op_bf", pos)
            else:
                # Destroy all cards based on power
                for pos in valid_targets["yu_bf"]:
                    card_power = self.bfield[pos]['card'].power
                    if card_power <= power:
                        self.a_move_to_graveyard(set, pos)
                for pos in valid_targets["op_bf"]:
                    card_power = self.opp_bfield[pos]['card'].power
                    if card_power <= power:
                        self.a_move_to_graveyard(set, pos)
            self.refresh_screen()
            self.post_effect()
        else:
            # Only selected targets will be destroyed
            filtered_targets = {"op_bf": [], "yu_bf": []}
            if power != None:
                # Filter out targets by power
                for pos in valid_targets["yu_bf"]:
                    card_power = self.bfield[pos].power
                    if card_power <= power:
                        filtered_targets["yu_bf"].append(pos)
                for pos in valid_targets["op_bf"]:
                    card_power = self.opp_bfield[pos].power
                    if card_power <= power:
                        filtered_targets["op_bf"].append(pos)
            else:
                filtered_targets = valid_targets

            if len(filtered_targets["yu_bf"]) == 0 and len(filtered_targets["op_bf"]) == 0:
                # No valid targets - do nothing
                return

            if opp_choice == None:
                # You will choose which cards to delete
                self.add_log(f"Select {count} targets from valid target list") # TODO: better log
                self.selected_card = []
                self.selected_card_choose = count
                self.select_mode = 1 # effect
                self.selected_card_targets = [("yu_bf", filtered_targets["yu_bf"]), ("op_bf", filtered_targets["op_bf"])]
                self.fun_queue.insert(0, (self.destroy_selected_creatures, []))
            else:
                # Opponent chooses which cards to delete
                self.add_log(f"Your opponent selects {count} targets to be removed") # TODO: better log
                args = []
                # invert sets
                for pos in filtered_targets["yu_bf"]:
                    args.append(SetName["op_bf"].value)
                    args.append(pos)
                for pos in filtered_targets["op_bf"]:
                    args.append(SetName["yu_bf"].value)
                    args.append(pos)
                self.your_turn = 0
                self.send_message(17, count, *args)

    def select_creatures_to_be_destoyed(self, count, target_list):
        self.add_log(f"Select {count} targets from valid target list") # TODO: better log
        self.your_turn = 2
        self.selected_card = []
        self.selected_card_choose = count
        self.select_mode = 1 # effect
        targets = {"yu_bf": [pos for (set, pos) in target_list if SetName(set).name == "yu_bf"], "op_bf": [pos for (set, pos) in target_list if SetName(set).name == "op_bf"]}
        self.selected_card_targets = [("yu_bf", targets["yu_bf"]), ("op_bf", targets["op_bf"])]
        self.fun_queue.insert(0, (self.destroy_selected_creatures, [True]))

    def destroy_selected_creatures(self, from_opp=False):
        for set, iden in self.selected_card:
            self.a_move_to_graveyard(set, iden)
        self.selected_card = []
        self.selected_card_choose = 0
        self.select_mode = 0
        self.selected_card_targets = []
        if from_opp:
            self.your_turn = 0
            self.send_message(117)
        self.refresh_screen()
        self.post_effect()

    def post_destroy_creatures(self):
        self.your_turn = 1
        self.refresh_screen()
        self.post_effect()
    
    def put_card_to_mana(self, mode, count, *args):
        if mode == "top":
            for _ in range(count):
                # Put a card from the top of your deck to mana
                card = self.a_get_top_card()
                self.add_log(f"You put {card.name} from the top of the deck to mana.")
                self.mana.add_card(card)
                self.send_message(7, 1, card.id)
            self.refresh_screen()
            self.post_effect()
            return
        elif mode == "opponentbf":
            if len(args) > 0 and args[0][0] == "opponentchoose":
                # Opponent chooses which cards to sacrafice to mana zone
                self.add_log(f"Your opponent selects {count} targets to be moved to mana zone from battlefield") # TODO: better log
                arguments = []
                for pos, _ in self.opp_bfield.get_creatures_with_pos():
                    arguments.append(SetName["yu_bf"].value)
                    arguments.append(pos)
                self.your_turn = 0
                self.send_message(20, count, *arguments)
            else:
                self.add_log(f"Select {count} targets from your opponent battlefield zone to be moved to mana zone")
                self.selected_card = []
                self.selected_card_choose = count
                self.select_mode = 1 # effect
                self.selected_card_targets = [("op_bf", ["*"])]
                self.fun_queue.insert(0, (self.put_to_mana_selected_creatures, []))
            return
        elif mode == "battlefield":
            self.add_log(f"Select {count} targets from your battlefield zone to be sacraficed to mana zone")
            self.selected_card = []
            self.selected_card_choose = count
            self.select_mode = 1 # effect
            self.selected_card_targets = [("yu_bf", ["*"])]
            self.fun_queue.insert(0, (self.put_to_mana_selected_creatures, []))
            return
        cards = []
        if mode == "graveyard":
            cards = [card.id for card in self.graveyard]
        elif mode == "hand":
            cards = [card.id for card in self.hand]
        settings = {"cards": cards, "count": count}
        self.cards_window = CommonWindow(settings, self)
        self.cards_window.card_choosed.connect(lambda: self.post_put_card_to_mana(mode))
        self.cards_window.show()

    def post_put_card_to_mana(self, mode):
        # TODO: better doc
        for card_id in self.cards_window.get_selected_items():
            card = self.database.get_card(card_id)
            if mode == "graveyard":
                self.graveyard.remove_card(card)
                self.add_log(f"Added card {card.name} from graveyard to mana")
                self.send_message(7, 2, card_id)
                self.mana.add_card(card)
            elif mode == "hand":
                self.hand.remove_card_by_id(card)
                self.add_log(f"Added card {card.name} from hand to mana")
                self.send_message(7, 0, card_id)
                self.mana.add_card(card)
        self.refresh_screen()
        self.post_effect()

    def select_creatures_to_be_put_to_mana(self, count, target_list): # TODO: change sacrafice, reserved for removing mana/creatures to play a card
        self.add_log(f"Select {count} targets from valid target list") # TODO: better log
        self.your_turn = 2
        self.selected_card = []
        self.selected_card_choose = count
        self.select_mode = 1 # effect
        targets = {"yu_bf": [pos for (set, pos) in target_list if SetName(set).name == "yu_bf"]}
        self.selected_card_targets = [("yu_bf", targets["yu_bf"])]
        self.fun_queue.insert(0, (self.put_to_mana_selected_creatures, [True]))

    def put_to_mana_selected_creatures(self, from_opp=False): # TODO: change sacrafice, reserved for removing mana/creatures to play a card
        for set, iden in self.selected_card:
            if set == "yu_bf":
                card = self.bfield.remove_card(iden)
                self.mana.add_card(card)
                self.send_message(21, 0, iden)
            elif set == "op_bf":
                card = self.opp_bfield.remove_card(iden)
                self.opp_mana.add_card(card)
                self.send_message(21, 1, iden)
        self.selected_card = []
        self.selected_card_choose = 0
        self.select_mode = 0
        self.selected_card_targets = []
        if from_opp:
            self.your_turn = 0
            self.send_message(120)
        self.refresh_screen()
        self.post_effect()

    def post_sacrafice_creatures(self): # TODO: change sacrafice, reserved for removing mana/creatures to play a card
        self.your_turn = 1
        self.refresh_screen()
        self.post_effect()

    def tap_creature(self, firsttime, mode, count=0):
        if firsttime:
            if mode == "count":
                self.add_log(f"Choose {count} cards in the battlefield to activate the effect.")
                self.selected_card_choose = count
                self.selected_card_targets = [("op_bf", ["*"])]
                self.selected_card = []
                self.fun_queue.insert(0, (self.tap_creature, [False, mode]))
                self.select_mode = 1
            elif mode == "fullboard":
                for pos, _ in self.opp_bfield.get_creatures_with_pos():
                    self.opp_bfield.set_tapped(pos)
                    self.send_message(16, 0, 1, pos)
                self.add_log(f"All opponents creature have been tapped.")
                self.refresh_screen()
                self.post_effect()
        else:
            for card in self.selected_card:
                self.opp_bfield.set_tapped(card[1])
                self.send_message(16, 0, 1, card[1])
            log_string = ", ".join([str(card[1]) for card in self.selected_card])
            self.add_log(f"{log_string} opponents creature have been tapped.")
            self.selected_card = []
            self.selected_card_targets = []
            self.select_mode = 0
            self.refresh_screen()
            self.post_effect()

    def one_for_one(self, count):
        # Unique effect of Rothus
        self.add_log(f"Select {count} targets from valid target list") # TODO: better log
        self.your_turn = 2
        self.selected_card = []
        self.selected_card_choose = count
        self.select_mode = 1 # effect
        self.selected_card_targets = [("yu_bf", ["*"])]
        self.fun_queue.insert(0, (self.destroy_selected_creatures, []))
        self.fun_queue.insert(1, (self.one_for_one_opponent, [count]))

    def one_for_one_opponent(self, count):
        # Opponent chooses which cards to delete
        self.add_log(f"Your opponent selects {count} targets to be removed") # TODO: better log
        args = []
        # invert sets
        for pos, _ in self.opp_bfield.get_creatures_with_pos():
            args.append(SetName["yu_bf"].value)
            args.append(pos)
        self.your_turn = 0
        self.send_message(17, count, *args)

    def discard_cards(self, count):
        # Opponent discards x cards from his hand
        for _ in range(count):
            if len(self.opp_hand) > 0:
                pos = self.opp_hand.return_random()
                self.a_move_to_graveyard("op_hd", pos)
        self.post_effect()

    def sacrifice_creature(self, count):
        self.add_log(f"Select {count} targets from valid target list") # TODO: better log
        self.your_turn = 2
        self.selected_card = []
        self.selected_card_choose = count
        self.select_mode = 1 # effect
        self.selected_card_targets = [("yu_bf", ["*"])]
        self.fun_queue.insert(0, (self.destroy_selected_creatures, []))

    def sacrifice_mana(self, count):
        # TODO: show locked mana in common view 
        cards = [card.id for card in self.mana]
        settings = {"cards": cards, "count": count}
        self.cards_window = CommonWindow(settings, self)
        self.cards_window.card_choosed.connect(self.post_sacrifice_mana)
        self.cards_window.show()

    def post_sacrifice_mana(self):
        offset = 0
        for pos in sorted(self.cards_window.get_selected_cards()):
            self.a_move_to_graveyard("yu_mn", pos - offset)
            offset += 1
        self.refresh_screen()
        self.post_effect()

    def treat_card_as_tapped(self, count):
        self.add_log(f"Select {count} targets from valid target list") # TODO: better log
        self.your_turn = 2
        self.selected_card = []
        self.selected_card_choose = count
        self.select_mode = 1 # effect
        self.selected_card_targets = [("op_bf", ["*"])]
        self.fun_queue.insert(0, (self.post_treat_card_as_tapped, []))
    
    def post_treat_card_as_tapped(self):
        for _, iden in self.selected_card:
            self.opp_bfield.give_effect(iden, "turn", "treatastapped")
            self.send_message(23, iden, 1, EffectName["treatastapped"].value)
        self.selected_card = []
        self.selected_card_choose = 0
        self.select_mode = 0
        self.selected_card_targets = []
        self.refresh_screen()
        self.post_effect()

    def give_effect(self, mode, count, effects):
        # TODO: better log, list effects etc.
        self.add_log(f"Select {count} targets from valid target list") 
        self.your_turn = 2
        self.selected_card = []
        self.selected_card_choose = count
        self.select_mode = 1 # effect
        self.selected_card_targets = [("yu_bf", ["*"])]
        self.fun_queue.insert(0, (self.post_give_effect, [mode, effects]))

    def post_give_effect(self, mode, effects):
        for effect_name in effects.keys():
            arguments = []
            for arg, value in effects[effect_name].items():
                arguments.append((arg, value))
            for _, iden in self.selected_card:
                self.bfield.give_effect(iden, mode, effect_name, *arguments)
                self.send_message(23, iden, 0, EffectName[effect_name].value)
        self.selected_card = []
        self.selected_card_choose = 0
        self.select_mode = 0
        self.selected_card_targets = []
        self.refresh_screen()
        self.post_effect()

    ##################
    #  GAME METHODS  #
    ##################

    def a_get_top_card(self):
        """Draw a top card from your deck and return it"""
        if not len(self.deck) == 0:
            card_id = self.deck.pop(0)
            card = self.database.get_card(card_id)
        else:
            self.add_log("You don't have enough cards to draw from. You lose!")
            self.lose()
        return card

    def a_draw_card(self):
        """Draw a top card from your deck and add it to your hand"""
        # Check if you are allowed to draw a card
        if self.card_to_draw == 0:
            return
        card = self.a_get_top_card()
        self.add_log("You draw a card {}.".format(card.name))
        self.hand.add_card(card)
        self.send_message(3)
        self.card_to_draw -= 1
        self.refresh_screen()

    def a_end_turn(self):
        """End your turn"""
        for pos, card in self.bfield.get_creatures_with_pos():
            if self.bfield.has_effect("mustattack", pos):
                # check if creature attacked, if not, print message and skip end turn
                if not self.bfield.is_tapped(pos) and not self.bfield.has_summon_sickness(pos):
                    self.add_log(f"You still have {card.name} that must attack this turn.")
                    return
        self.add_log("End of your turn.")
        self.send_message(2)

        # TODO: for now by default untap, later there can be choice
        for card_pos, card in self.bfield.get_creatures_with_pos():
            for pos_effect, effect in enumerate(card.effects):
                # untap effect
                if "untap" in effect:
                    mode = effect["untap"]["mode"]
                    if mode == "self":
                        # Untap itself
                        self.bfield.set_untapped(card_pos)
                        break
                    elif mode == "all":
                        # Untap all your cards
                        for pos, _ in self.bfield.get_creatures_with_pos():
                            self.bfield.set_untapped(pos)
                        break
                # expire effect by one turn
                if "time" in list(effect.values())[0]:
                    if list(effect.values())[0]["time"] != "-":
                        self.bfield.decrement_time_for_effect(card_pos, pos_effect)
        for card_pos, card in self.opp_bfield.get_creatures_with_pos():
            for pos_effect, effect in enumerate(card.effects):
                # expire effect by one turn
                if "time" in list(effect.values())[0]:
                    if list(effect.values())[0]["time"] != "-":
                        self.opp_bfield.decrement_time_for_effect(card_pos, pos_effect)
        self.bfield.handle_expired_effects()
        self.opp_bfield.handle_expired_effects()

        self.selected_card = []
        self.your_turn = 0
        
    def a_summon_card(self, iden):
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
            # TODO: print some info that more or less mana must be tapped instead of doing nothing
            # Not enough mana tapped, too much mana tapped -> do nothing
            return
        self.refresh_screen()

    def a_choose_card(self, set, iden):
        # Action: Choose a card as a target for e.g. effect, attack
        if [set, iden] in self.selected_card:
            # can't choose the same card twice
            return
        # TODO: if not effect or spell targeting, if selected_card is creature set to him shield count
        self.selected_card.append([set, iden])
        # if set == 'yu_bf':
        #     if "shieldbreaker" in self.bfield[iden].effects:
        #         count = int(self.bfield[iden].effects["shieldbreaker"]["count"])
        #     else:
        #         count = 1
        #     self.bfield.set_shield_count(iden, count)
        self.refresh_screen()

    def a_unchoose_card(self, set, iden):
        self.selected_card.remove((set, iden))
        self.refresh_screen()
        
    def a_return_card_to_hand(self, set, iden):
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
        
    def a_return_shield_to_hand(self, iden):
        # Action: Return your card under destroyed shield to hand
        card = self.shields.remove_shield(iden)
        self.hand.add_card(card)
        self.send_message(114, iden)
        self.shields_to_destroy.remove(iden)
        if len(self.shields_to_destroy) == 0:
            self.your_turn = 0
            self.send_message(314)
        else:
            self.add_log(f"You still have {len(self.shields_to_destroy)} shields to decide.")
        self.refresh_screen()

    def a_play_destroyed_shield(self, set, iden):
        # Action: Play a shield with shield trigger
        self.shields_to_destroy.remove(iden)
        card = self.shields.remove_shield(iden)
        self.send_message(214, iden)
        # TODO: somehow add check for len(self.shields_to_destroy) == 0 after handling summon
        if card.card_type == 'Spell':
            self.sfield.set_card(card)
            self.send_message(4, card.id, 5)
            self.spell_played = True
            self.summon_effect(card)
        elif card.card_type == 'Creature':
            # Handled in menu if there is space left
            pos = self.bfield.add_card(card)
            self.send_message(4, card.id, pos)
            self.summon_effect(card)
        self.refresh_screen()

    def a_move_to_graveyard(self, set, iden, send_message=True):
        # Action: Move a card to the graveyard
        if set == "yu_bf":
            card = self.bfield.remove_card(iden)
            moved = False
            for effect in card.effects:
                if "ondeath" in effect:
                    if effect["ondeath"]["mode"] == "tohand":
                        self.add_log(f"Your card {card.name} returned to your hand due to its effect.")
                        self.send_message(22, iden)
                        self.hand.add_card(card)
                        moved = True
                    elif effect["ondeath"]["mode"] == "tomana":
                        self.add_log(f"Your card {card.name} was moved to your mana due to its effect.")
                        self.send_message(21, 0, iden)
                        self.mana.add_card(card)
                        moved = True
            if not moved: # check if card was earlier handled by ondeath effect
                self.add_log(f"Your card {card.name} was sent to graveyard.")
                self.graveyard.add_card(card)
                self.send_message(6, 1, 1, iden)
        elif set == "yu_sf":
            card = self.sfield.remove_card()
            self.graveyard.add_card(card)
            self.add_log(f"Your card {card.name} was sent to graveyard.")
            self.send_message(6, 1, 1, 5)
        elif set == "yu_mn":
            card = self.mana.remove_card(iden)
            self.graveyard.add_card(card)
            self.add_log(f"Your card {card.name} from mana zone was moved to your graveyard.")
            self.send_message(6, 1, 0, iden)
        elif set == "yu_hd":
            card = self.hand.remove_card(iden)
            self.graveyard.add_card(card)
            self.add_log(f"Your card {card.name} from hand was discarded to your graveyard.")
            self.send_message(6, 1, 2, iden)
        elif set == "op_mn":
            card = self.opp_mana.remove_card(iden)
            self.opp_graveyard.add_card(card)
            self.add_log(f"Opponent's card {card.name} from mana zone was moved to his graveyard.")
            if send_message:
                self.send_message(6, 0, 0, iden)
        elif set == "op_bf":
            # Just sent a message to destroy that card
            # Opponent will return where it went
            self.send_message(6, 0, 1, iden)
        elif set == "op_sf":
            card = self.opp_sfield.remove_card()
            self.opp_graveyard.add_card(card)
            self.add_log(f"Opponent's card {card.name} was sent to graveyard.")
            self.send_message(6, 0, 1, 5)
        elif set == "op_hd":
            self.opp_hand.remove_card(iden)
            # Opponent will sent which card was sent to graveyard
            self.send_message(6, 0, 2, iden)
        self.refresh_screen()
        
    def a_add_to_mana(self, iden):
        if self.card_to_mana > 0:
            card = self.hand.remove_card(iden)
            self.mana.add_card(card)
            self.card_to_mana -= 1
            self.send_message(7, 0, card.id)
            self.refresh_screen()
        
    def a_add_to_shield(self, iden):
        card = self.hand.remove_card(iden)
        pos = self.shields.add_shield(card)
        self.send_message(8, pos)
        self.refresh_screen()
        
    def a_tap_mana(self, set, iden):
        if not self.mana.is_tapped(iden):
            self.mana.tap_card(iden)
            self.send_message(9, 1, iden)
        self.refresh_screen()
        
    def a_untap_mana(self, set, iden):
        if self.mana.is_tapped(iden):
            self.mana.untap_card(iden)
            self.send_message(9, 0, iden)
        self.refresh_screen()
        
    def a_look_at_shield(self, iden):
        self.shields.set_shield_visible(iden)
        self.send_message(10, iden)
        self.refresh_screen()

    def a_put_shield(self, iden):
        # TODO: implement this as action on the end of turn if shield was revealed
        # self.shields[iden-1][1] = True
        self.refresh_screen()
        
    def a_select_creature(self, set, iden):
        # Action: select your creature to attack another creature or shield
        # TODO: check if creature can attack (ability, tapped)
        if self.bfield.is_tapped(iden):
            return
        if set == 'yu_bf':
            count = 1
            if self.bfield.has_effect("shieldbreaker", iden):
                for effect in self.bfield[iden].effects:
                    if list(effect.keys())[0] == "shieldbreaker":
                        if count < int(effect["shieldbreaker"]["count"]):
                            count = int(effect["shieldbreaker"]["count"])
            self.bfield.set_shield_count(iden, count)
        self.selected_card = [(set, iden)]
        self.selected_shields = []
        self.select_mode = 2

    def a_unselect_creature(self, set, iden):
        # Action: unselect your creature to attack another creature or shield
        self.selected_card.remove((set, iden))
        self.selected_shields = []
        self.select_mode = 0

    def a_attack_creature(self, set, iden):
        # Action: attack creature with your creature
        if len(self.selected_card) == 0 or not self.select_mode == 2: 
            # None of the attacking creatures is selected
            return
        # if not self.opp_bfield.is_tapped(iden) and True: # checks already done on views/card level
        #     return
        self.add_log(f"Attacking card {self.opp_bfield[iden].name} with card {self.bfield[self.selected_card[0][1]].name}")
        self.send_message(12, self.selected_card[0][1], iden) # Inform opponent about the attack
        self.your_turn = 0

    def a_select_shield_to_attack(self, iden):
        if iden in self.selected_shields:
            return
        self.selected_shields.append(iden)
        self.select_mode = 21

    def a_remove_shield_to_attack(self, iden):
        self.selected_shields.remove(iden)

    def a_shield_attack(self):
        if len(self.selected_card) == 0 or not self.select_mode == 21:
            return
        self.add_log(f"Attacking shields {self.selected_shields} with card {self.bfield[self.selected_card[0][1]].name}")
        self.send_message(13, self.selected_card[0][1], *self.selected_shields)
        self.select_mode = 0
        self.your_turn = 0

    def a_block_with_creature(self, set, iden):
        self.add_log(f"Blocking attack with {iden}")
        self.your_turn = 0
        self.blocker_list = []
        self.send_message(112, iden)

    def a_pass_attack(self): 
        self.add_log(f"Passing blocking")
        self.your_turn = 0
        self.blocker_list = []
        self.send_message(112, self.chosen)

    def a_shield_block_with_creature(self, set, iden):
        self.add_log(f"Blocking attack with {iden}")
        self.your_turn = 0
        self.blocker_list = []
        self.send_message(113, iden)

    def a_shield_pass_attack(self): 
        self.add_log(f"Passing blocking")
        self.your_turn = 0
        self.blocker_list = []
        self.send_message(113)
    
    def a_direct_attack(self):
        # Action: direct attack to another player
        # All checks done on views/game level
        iden = self.get_selected_card()[0][1]
        self.add_log(f"Attacking player directly")
        self.send_message(24, iden)

    def a_direct_block_with_creature(self, set, iden):
        self.add_log(f"Blocking attack with {iden}")
        self.your_turn = 0
        self.blocker_list = []
        self.send_message(124, iden)
   
    def a_opp_look_at_hand(self, iden):
        self.send_message(11, 0, iden)
        
    def a_opp_look_at_shield(self, iden):
        self.send_message(11, 1, iden)
        
    def a_look_graveyard(self, set):
        if set == "op_gv":
            graveyard_look = GraveyardWindow(self.opp_graveyard, self)
        elif set == "yu_gv":
            graveyard_look = GraveyardWindow(self.graveyard, self)
        else:
            return
        graveyard_look.show()

#### DEBUG ACTIONS
    def a_debug_info(self):
        print("====DEBUG====")
        print(f"your_turn: {self.get_your_turn()}")
        print(f"select_mode: {self.get_select_mode()}")
        print(f"selected_card: {self.get_selected_card()}")
        print(f"selected_shields: {self.get_selected_shields()}")
        print(f"selected_card_targets: {self.get_selected_card_targets()}")
        print(f"selected_card_choose: {self.get_selected_card_choose()}")
        print(f"your_bf: {self.get_your_bf()}")
        print(f"your_mn: {self.get_your_mn()}")
        print(f"your_mn_weights: {self.mana.weights}")
        print("=============")