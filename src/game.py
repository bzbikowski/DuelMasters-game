import logging
import random

from PySide2.QtCore import Qt, QTimer, QThread, Slot, Signal
from PySide2.QtGui import QBrush, QColor, QPen, QPixmap, QTransform, QImage, QFont
from PySide2.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, \
    QTextEdit, QLabel, QPushButton, QGraphicsRectItem, QGraphicsTextItem, QMessageBox

from src.cards import ParseXml
from src.logs import Logger
from src.network.client import Client
from src.network.server import Server
from src.views import GameView, CardView, GraveyardView
from src.serverdialog import ServerDialog
from src.clientdialog import ClientDialog
from src.controller import Controller
from src.ui.ui_game import Ui_Game


class Game(QWidget):
    """
    Main class in application.
    """
    yourTurn = Signal(bool)
    def __init__(self, mode, deck, database, debug, parent=None):
        # todo change to sqlite
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
        self.your_turn = False
        self.selected_card = None
        self.focus_request = False
        self.select_mode = False
        self.card_to_choose = 0
        self.turn_count = 0

        self.view_scene = GameView(self)
        self.ui.view.setScene(self.view_scene)
        self.view_scene.setBackgroundBrush(QBrush(QColor(0, 0, 0)))

        self.preview_scene = QGraphicsScene()
        self.ui.preview.setScene(self.preview_scene)
        self.preview_scene.setBackgroundBrush(QBrush(QColor(0, 0, 0)))

        self.log_panel = Logger()
        self.setup_logger()

        self.cardlist = ParseXml().parseFile('res/cards.xml')

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
        print("GAME - CLOSING")
        if self.started:
            if self.mode == 1:
                try:
                    self.server.close_connection()
                except RuntimeError:
                    print("Server already deleted")
            else:
                try:
                    self.client.disconnectFromHost()
                except RuntimeError:
                    print("Client already deleted")
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
                self.yourTurn.emit(False)
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
        self.dict_civ = {"Light": 0, "Nature": 1, "Darkness": 2, "Fire": 3, "Water": 4}
        random.shuffle(self.deck)
        self.shields = []
        for shield in self.deck[0:5]:
            self.shields.append([shield, True])
        self.deck = self.deck[5:]
        self.hand = self.deck[0:5]
        self.deck = self.deck[5:]
        self.mana = []
        self.weights = [0, 0, 0, 0, 0]
        self.bfield = [-1, -1, -1, -1, -1, -1]
        self.graveyard = []
        self.opp_shields = [True, True, True, True, True]
        self.opp_mana = []
        self.opp_hand = [-1, -1, -1, -1, -1]
        self.opp_bfield = [-1, -1, -1, -1, -1, -1]
        self.opp_graveyard = []
        self.background = QGraphicsPixmapItem(QPixmap("res//img//background.png"))
        self.view_scene.addItem(self.background)
        self.preview_scene.addItem(QGraphicsPixmapItem(QPixmap("res//img//console.png")))
        self.extend_logs_button = QPushButton()
        self.extend_logs_button.setFixedSize(20, 20)
        self.extend_logs_button.clicked.connect(self.change_logs_size)
        self.proxy = self.preview_scene.addWidget(self.extend_logs_button)
        self.change_button_state = True
        self.selected_card = []

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
        self.add_shield_to_scene(self.shields, "yu_sh")
        # opponent's shields
        self.add_shield_to_scene(self.opp_shields, "op_sh")
        # your battlefield
        self.add_bf_to_scene(self.bfield, "yu_bf")
        # opponent's battlefield
        self.add_bf_to_scene(self.opp_bfield, "op_bf")
        # your graveyard
        if not len(self.graveyard) == 0:
            card = CardView("yu_gv", 1, self)
            item = self.find_card(self.graveyard[len(self.graveyard) - 1])
            card.set_card(item)
            card.setPixmap(self.get_pixmap_card(self.graveyard[len(self.graveyard) - 1]))
            card.setPos(866, 639)
            self.view_scene.addItem(card)
        # opponent's graveyard
        if not len(self.opp_graveyard) == 0:      
            card = CardView("op_gv", 1, self)
            item = self.find_card(self.opp_graveyard[len(self.opp_graveyard) - 1])
            card.set_card(item)
            transform = QTransform().rotate(180)
            card.setPixmap(self.get_pixmap_card(self.opp_graveyard[len(self.opp_graveyard) - 1]).transformed(transform))
            card.setPos(74, 14)
            self.view_scene.addItem(card)
        # your cards in hand
        self.add_hand_to_scene(self.hand, "yu_hd")
        # opponent's cards in hand
        self.add_hand_to_scene(self.opp_hand, "op_hd")
        # your cards in mana zone
        self.add_mana_to_scene(self.mana, "yu_mn")
        # opponent's cards in mana zone
        self.add_mana_to_scene(self.opp_mana, "op_mn")
        # change max number of logs to display
        if self.change_button_state:
            self.extend_logs_button.setText("+")
            self.proxy.setPos(20, 540)
        else:
            self.extend_logs_button.setText("*")
            self.proxy.setPos(20, 20)
        # display logs
        if not len(self.log_panel) == 0:
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
                ramka = QGraphicsRectItem(x_pos, y_pos, x_width, y_height)
                ramka.setPen(QPen(QColor(255, 0, 0)))
                self.preview_scene.addItem(ramka)

                tekst = QGraphicsTextItem(log)
                tekst.setPos(x_pos + 10, y_pos + 5)
                tekst.setTextWidth(x_width-20)
                self.preview_scene.addItem(tekst)
                y_pos -= 60

    def get_pixmap_card(self, card_id, res='low_res'):
        """Get pixmap of card from the database"""
        pixmap = QPixmap()
        if not pixmap.loadFromData(self.database.getdata(card_id, res)):
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
        pixmap = self.get_pixmap_card(card_id, 'high_res')
        card_prev = QGraphicsPixmapItem(pixmap)
        card_prev.setPos(0, 0)
        self.preview_scene.addItem(card_prev)
        
    def add_hand_to_scene(self, arr, type):
        """
        Draw card from hand into the screen
        """
        x = 0
        height = 0
        if type == "yu_hd":
            height = 639
        elif type == "op_hd":
            height = 14
        size = len(arr)
        for i in range(size):
            item = CardView(type, i + 1, self)
            if arr[i] == -1:
                link = "res//img//cardback.png"
                pixmap = QPixmap(link)
            else:
                pixmap = self.get_pixmap_card(arr[i])
                card = self.find_card(arr[i])
                item.set_card(card)
            if type == "op_hd":
                transform = QTransform().rotate(180)
                pixmap = pixmap.transformed(transform)
            item.setPixmap(pixmap)
            if size <= 6:
                if size % 2 == 0:
                    x = 422 - 95 * (size/2 - 1) + i * 95
                    item.setPos(422 - 95 * (size/2 - 1) + i * 95, height)
                else:
                    x = 512 - 85 / 2 - 95 * ((size - 1) / 2) + 95 * i
                    item.setPos(512 - 85 / 2 - 95 * ((size - 1) / 2) + 95 * i, height)
            else:
                x = 232 + (475 / (size - 1)) * i
            item.setPos(x, height)
            self.view_scene.addItem(item)
            if not len(self.selected_card) == 0:
                for sel_card in self.selected_card:
                    if sel_card[0] == type:
                        if sel_card[1] == i + 1:
                            self.highlight_card(x, x + 85, height, height + 115, QColor(0, 0, 255))
                            break
            
    def add_mana_to_scene(self, arr, type):
        """
        Draw card from mana into the screen
        """
        x = 0
        height = 0
        if type == "yu_mn":
            height = 514
        elif type == "op_mn":
            height = 139
        size = len(arr)
        for i in range(size):
            item = CardView(type, i + 1, self)
            card = self.find_card(arr[i][0])
            item.set_card(card)
            pixmap = self.get_pixmap_card(arr[i][0])
            # pixmap = QPixmap(card.image)
            if type == "yu_mn":
                transform = QTransform().rotate(180)
                pixmap = pixmap.transformed(transform)
            if not arr[i][1]:
                image = pixmap.toImage()
                image = image.convertToFormat(QImage.Format_Grayscale8)
                pixmap = pixmap.fromImage(image)
            item.setPixmap(pixmap)
            if size <= 6:
                if size % 2 == 0:
                    x = 422 - 95 * (size/2 - 1) + i * 95
                else:
                    x = 512 - 85 / 2 - 95 * ((size - 1) / 2) + 95 * i
            else:
                x = 232 + (475 / (size - 1)) * i
            item.setPos(x, height)
            self.view_scene.addItem(item)
            if not len(self.selected_card) == 0:
                for sel_card in self.selected_card:
                    if sel_card[0] == type:
                        if sel_card[1] == i + 1:
                            self.highlight_card(x, x + 85, height, height + 115, QColor(0, 0, 255))
                            break

    def add_shield_to_scene(self, arr, type):
        """
        Draw shield into the screen
        """
        for i in range(len(arr)):
            x = y = 0
            if type == "yu_sh":
                x = 866
                y = 14
                if not arr[i][0] == -1:
                    card = CardView("yu_sh", i + 1, self)
                    if arr[i][1]:
                        card.setPixmap(QPixmap("res//img//cardback.png"))
                    else:
                        item = self.find_card(arr[i][0])
                        card.set_card(item)
                        pixmap = self.get_pixmap_card(arr[i][0])
                        card.setPixmap(pixmap)
                    card.setPos(x, y + i * 125)  # tarcze twoje
                    self.view_scene.addItem(card)
            elif type == "op_sh":
                x = 74
                y = 139
                if arr[i]:
                    card = CardView("op_sh", i + 1, self)
                    transform = QTransform().rotate(180)
                    pixmap = QPixmap("res//img//cardback.png").transformed(transform)
                    card.setPixmap(pixmap)
                    card.setPos(x, y + i * 125)
                    self.view_scene.addItem(card)
            if not len(self.selected_card) == 0:
                for sel_card in self.selected_card:
                    if sel_card[0] == type:
                        if sel_card[1] == i + 1:
                            self.highlight_card(x, x + 85, y, y + 115, QColor(0, 0, 255))
                            break

    def add_bf_to_scene(self, arr, type):
        """
        Draw card from battlefield into the screen
        """
        x = 232
        y = 0
        if type == "yu_bf":
            y = 389
        elif type == "op_bf":
            y = 264
        for i in range(len(arr)):
            if not arr[i] == -1:
                card = CardView(type, i + 1, self)
                item = self.find_card(arr[i])
                card.set_card(item)
                pixmap = self.get_pixmap_card(arr[i])
                card.setPixmap(pixmap)
                card.setPos(x + i * 95, y)
                self.view_scene.addItem(card)

            if not len(self.selected_card) == 0:
                for sel_card in self.selected_card:
                    print(f"SELECTED CARD: {sel_card[0]} {sel_card[1]}; i + 1 = {i + 1}")
                    if sel_card[0] == type:
                        if sel_card[1] == i + 1:
                            self.highlight_card(x, x + 85, y, y + 115, QColor(0, 0, 255))
                            break

    def add_log(self, msg, refresh=True):
        """Add log to log panel"""
        self.log_panel.append(msg)
        if refresh:
            self.refresh_screen()

    def find_card(self, iden):
        """
        Find informations about card of given id
        :param iden:  id of the card
        :return: Card class with all informations about it
        """
        for card in self.cardlist:
            if card.id == iden:
                return card

    def send_message(self, *msg):
        """
        Messages, which are sent to opponent:
        0 - you start the game
        1 - przeciwnik zaczyna grę
        2 - koniec mojej tury
        3 - ja dobieram kartę
        4,x,y - ja zagrywam kartę o id x na miejscu y na pole bitwy
        5,v,x,y - gracz v podnosi kartę z pól x z miejsca y do ręki
                  v - 0/1 - przeciwnik/ty
                  x - 0/1 - mana/pole bitwy
        6,v,x,y - gracz v podnosi kartę z pól x z miejsca y na cmentarz
                  v - 0/1 - przeciwnik/ty
                  x - 0/1 - mana/pole bitwy
        7,x - ja dodaję kartę x z ręki na mane
        8,x,y - ja dodaję kartę x z reki na tarczę y
        9,x,y - ja tapuje/odtapuje manę
                x - 0/1 - odtapuje/tapuje
                y - pozycja karty na manie
        10,x - ja zaglądam w swoją tarczę na pozycji x
        11,x,y - ja zaglądam w twoją tarczę/kartę z reki na pozycji y
                x - 0/1 - ręka/tarcza
        12,x,y - (info) ja atakuje swoją kartą x twoją kartę y na polu bitwy
        13,x - ja niszcze ci tarczę na pozycji x
        """
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
        # TODO: unlock and untap all your mana
        if state == 1:
            self.card_to_draw = 1
            self.m_draw_a_card()
        self.card_to_mana = 1
        self.your_turn = True
        self.yourTurn.emit(True)

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

    def summon_effect(self, card_id):
        """Check and trigger the effects of played card"""
        # TODO: debug this
        card = self.find_card(card_id)
        print(f"Effects of card {card}: {str(card.effects)}")
        for effect in card.effects:
            if "teleport" in effect.keys():
                count = int(effect["teleport"]["count"])
                print(f"Teleport {count}")
                self.teleport(True, count)
            if "destroy_blockers" in effect.keys():
                if effect["destroy_blockers"]["mode"] == "all":
                    self.destroy_blocker(-1)

    def message_screen_request(self, bg_color, frame_color, text):
        """Message box for displaying important information. After one click it disappears."""
        # TODO: Debug why the box is not appearing
        bg = QGraphicsRectItem(100, 100, 200, 200)
        bg.setBrush(QBrush(bg_color))
        self.view_scene.addItem(bg)
        frame = QGraphicsRectItem(99, 99, 202, 202)
        frame.setPen(QPen(frame_color))
        self.view_scene.addItem(frame)
        text = QGraphicsTextItem(text)
        text.setPos(110, 110)
        self.view_scene.addItem(text)
        print("printed message box")
        self.focus_request = True
        self.select_mode = True

    #  EFFECT METHODS
    #####################################################

    def teleport(self, firsttime, count=0):
        if firsttime:
            print("First time teleport - show message screen")
            self.message_screen_request(QColor(55, 55, 55), QColor(255, 0, 0),
                                        f"Choose {count} cards in the battlefield to activate the effect.")
            self.card_to_choose = count
            self.type_to_choose = ["yu_bf", "op_bf"]
            self.fun_to_call = self.teleport
        else:
            print(f"Teleport this cards to hand: {self.selected_card}")
            for card in self.selected_card:
                self.m_return_card_to_hand(card[0], card[1])
            self.selected_card = []
            self.type_to_choose = []
            self.select_mode = False

    #   MENU METHODS
    #####################################################

    def m_draw_a_card(self):
        """Draw a top card from your deck and add it to your hand"""
        # Check if you are allowed to draw a card
        if self.card_to_draw == 0:
            return
        if not len(self.deck) == 0:
            card = self.deck.pop(0)
            self.add_log("You draw a card {}.".format(self.find_card(card).name))
            self.hand.append(card)
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
        self.your_turn = False
        self.yourTurn.emit(False)

    def m_accept_cards(self):
        print("ALL CARD SELECTED - TRIGGER ACTION")
        # TODO: it cannot be empty
        self.fun_to_call(False)
        
    def m_summon_card(self, iden):
        card = self.find_card(self.hand[iden - 1])
        sum = 0
        for item in self.weights:
            sum += item
        if sum >= int(card.cost) and not self.weights[self.dict_civ[card.civ]] == 0:
            # TODO: if card was summoned successfully, mark that mana as locked
            if card.typ == "Creature":
                for i in range(len(self.bfield) - 1):
                    # Look for free space on the board (value -1)
                    if self.bfield[i] == -1:
                        card = self.hand.pop(iden - 1)
                        self.bfield[i] = card
                        self.log.info(f"You've played a creature {card}")
                        self.add_log(f"You have played {card} on position {i}")
                        self.send_message(4, card, i)
                        self.summon_effect(card)
                        break
            elif card.typ == "Spell":
                # Spells are played on 6th space, separate of creature ones
                if self.bfield[5] == -1:
                    card = self.hand.pop(iden - 1)
                    self.bfield[5] = card
                    self.log.info(f"You've played a spell {card}")
                    self.add_log(f"You have played spell {card}")
                    self.send_message(4, card, 5)
                    self.summon_effect(card)
        else:
            # Not enough mana tapped, do nothing
            return
        self.refresh_screen()

    def m_choose_card(self, set, iden):
        self.selected_card.append([set, iden])
        self.refresh_screen()
        
    def m_return_card_to_hand(self, set, iden):
        if set == "yu_bf":
            card = self.bfield[iden-1]
            self.bfield[iden-1] = -1
            self.hand.append(card)
            self.send_message(5, 1, 1, iden-1)
        elif set == "yu_mn":
            card = self.mana.pop(iden-1)
            if not card[1]:
                self.weights[self.dict_civ[self.find_card(card[0]).civ]] -= 1
            self.hand.append(card[0])
            self.send_message(5, 1, 0, iden-1)
        self.refresh_screen()
        
    def m_move_to_graveyard(self, set, iden):
        if set == "yu_bf":
            self.graveyard.append(self.bfield[iden - 1])
            self.bfield[iden - 1] = -1
            self.send_message(6, 1, 1, iden-1)
        elif set == "yu_mn":
            card = self.mana.pop(iden-1)
            if not card[1]:
                self.weights[self.dict_civ[self.find_card(card[0]).civ]] -= 1
            self.graveyard.append(card[0])
            self.send_message(6, 1, 0, iden - 1)
        self.refresh_screen()
        
    def m_add_to_mana(self, iden):
        if self.card_to_mana > 0 or self.debug_mode:
            card = self.hand.pop(iden-1)
            self.mana.append([card, True])
            self.card_to_mana -= 1
            self.send_message(7, card)
            self.refresh_screen()
        
    def m_add_to_shield(self, iden):
        for i, shield in enumerate(self.shields):
            if shield[0] == -1:
                card = self.hand.pop(iden-1)
                self.shields[i][0] = card
                self.send_message(8, card, i)
                break
        self.refresh_screen()
        
    def m_tap_card(self, set, iden):
        if self.mana[iden - 1][1]:
            card = self.find_card(self.mana[iden - 1][0])
            self.weights[self.dict_civ[card.civ]] += 1
            self.mana[iden - 1][1] = False
            self.send_message(9, 1, iden - 1)
        self.refresh_screen()
        
    def m_untap_card(self, set, iden):
        if self.mana[iden - 1][1] == False:
            card = self.find_card(self.mana[iden - 1][0])
            self.weights[self.dict_civ[card.civ]] -= 1
            self.mana[iden - 1][1] = True
            self.send_message(9, 0, iden - 1)
        self.refresh_screen()
        
    def m_look_at_shield(self, iden):
        self.shields[iden-1][1] = False
        self.send_message(10, iden-1)
        self.refresh_screen()
        
    def m_attack_with_creature(self, iden):
        self.selected_card = [self.bfield[iden-1], iden-1]
        
    def m_attack_opp_creature(self, iden):
        if self.selected_card is not None:
            opp_card = self.opp_bfield[iden-1]
            if self.cardlist[opp_card].power < self.cardlist[self.selected_card[0]].power:
                #trafiony zatopiony
                self.send_message(6, 0, 1, iden-1)
            elif self.cardlist[opp_card].power == self.cardlist[self.selected_card[0]].power:
                #oba zniszczone
                self.send_message(6, 0, 1, iden-1)
                self.send_message(6, 1, 1, self.selected_card[1])
            else:
                self.send_message(6, 1, 1, self.selected_card[1])
                #giniesz
            self.send_message(12, self.selected_card[0], opp_card)
        
    def m_opp_look_at_hand(self, iden):
        self.send_message(11, 0, iden)
        
    def m_opp_look_at_shield(self, iden):
        self.send_message(11, 1, iden)
        
    def m_opp_return_card_to_hand(self, set, iden):
        if set == "op_mn":
            self.opp_mana.pop(iden-1)
            self.send_message(5, 0, 0, iden - 1)
        elif set == "op_bf":
            self.opp_bfield[iden - 1] = -1
            self.send_message(5, 0, 1, iden - 1)
        self.opp_hand.append(-1)
        self.refresh_screen()
        
    def m_opp_move_to_graveyard(self, set, iden):
        if set == "op_mn":
            self.opp_graveyard.append(self.opp_mana.pop(iden-1)[0])
            self.send_message(6, 0, 0, iden - 1)
        elif set == "op_bf":
            self.opp_graveyard.append(self.opp_bfield[iden - 1])
            self.opp_bfield[iden - 1] = -1
            self.send_message(6, 0, 1, iden - 1)
        self.refresh_screen()
        
    def m_opp_shield_attack(self, iden):
        if self.selected_card is not None:
            # todo sprawdz czy moze atakować i czy przeciwnik ma blokery
            pass

            if self.opp_shields[iden-1]:
                self.send_message(13, iden-1)
        
    def m_look_graveyard(self, set):
        if set == "op_gv":
            graveyard_look = GraveyardView(self.opp_graveyard, self)
        elif set == "yu_gv":
            graveyard_look = GraveyardView(self.graveyard, self)
        else:
            return
        graveyard_look.show()
        
    def m_put_shield(self, iden):
        self.shields[iden-1][1] = True
        self.refresh_screen()
