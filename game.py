from PyQt5.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem, QMenu, QAction, \
QTextEdit, QLabel, QPushButton, QGraphicsRectItem, QGraphicsTextItem
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QBrush, QColor, QPen, QPixmap, QTransform, QCursor, QImage, QFont
from cards import ParseXml
from views import GameView, CardView, GraveyardView
from connection import Client, Server
from logs import LogInfo
from collections import deque
import random


DEBUG = True


class Game(QWidget):
    def __init__(self, deck, parent=None):
        super(Game, self).__init__()
        width = 1360
        height = 768
        self.setFixedSize(width, height)
        #self.move((screen_width - self.width)/2, (screen_height - self.height)/2 - 20)
        self.setWindowTitle("Duel master - Game")
        self.locked = False
        self.isServer = False
        self.parent = parent
        self.deck = deck
        self.card_to_draw = 0
        self.card_to_mana = 0
        self.your_turn = False
        self.selected_card = None
        self.view = QGraphicsView(self)
        self.view.setSceneRect(0, 0, 1024, 768)
        self.view.setFixedSize(1024, 768)
        self.view.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.preview = QGraphicsView(self)
        self.preview.move(1024, 0)
        self.preview.setFixedSize(336, 768)
        self.preview.setSceneRect(0, 0, 336, 768)
        self.preview.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.preview.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.view_scene = GameView(self)
        self.view.setScene(self.view_scene)
        self.view_scene.setBackgroundBrush(QBrush(QColor(0, 0, 0)))
        self.view.setVisible(False)

        self.preview_scene = QGraphicsScene()
        self.preview.setScene(self.preview_scene)
        self.preview_scene.setBackgroundBrush(QBrush(QColor(0, 0, 0)))
        self.preview.setVisible(False)

        self.logs = deque(maxlen=10)

        self.card_prev = None

        self.cardlist = ParseXml().parseFile('res/cards.xml')
        self.choose_connection()

    def closeEvent(self, event):
        if self.isServer:
            self.server.wait()
        else:
            self.client.wait()
        self.parent.show_window()

    def choose_connection(self):
        self.server_button = QPushButton("Create a game room", self)
        self.server_button.setFixedSize(1000, 300)
        self.server_button.move((self.width() - self.server_button.width())/2, 40)
        self.server_button.clicked.connect(self.wait_for_connection)
        self.server_button.setFont(QFont("Arial", 60))
        self.client_button = QPushButton("Connect to existing game", self)
        self.client_button.setFixedSize(1000, 300)
        self.client_button.move((self.width() - self.client_button.width()) / 2, 420)
        self.client_button.clicked.connect(self.connect_to_room)
        self.client_button.setFont(QFont("Arial", 60))
        
    def connect_to_room(self):
        self.server_button.setVisible(False)
        self.client_button.setVisible(False)
        self.ip_address_label = QLabel("Ip address: ", self)
        self.ip_address_label.move(200, 150)
        self.ip_address_label.setFont(QFont("Arial", 50))
        self.ip_address_label.setVisible(True)
        self.ip_address_field = QTextEdit(self)
        self.ip_address_field.move(600, 150)
        self.ip_address_field.setFont(QFont("Arial", 50))
        self.ip_address_field.setFixedSize(550, 100)
        self.ip_address_field.setVisible(True)
        self.port_label = QLabel("Port: ", self)
        self.port_label.move(390, 360)
        self.port_label.setFont(QFont("Arial", 50))
        self.port_label.setVisible(True)
        self.port_field = QTextEdit(self)
        self.port_field.move(600, 360)
        self.port_field.setFont(QFont("Arial", 50))
        self.port_field.setFixedSize(550, 100)
        self.port_field.setVisible(True)
        self.ok_button = QPushButton("Accept", self)
        self.ok_button.setFixedSize(600, 140)
        self.ok_button.move((self.width() - self.ok_button.width())/2, 560)
        if DEBUG:
            self.ok_button.clicked.connect(self.connected_with_player)
        else:
            self.ok_button.clicked.connect(self.start_connection)
        self.ok_button.setVisible(True)

    def wait_for_connection(self):
        self.server_button.setVisible(False)
        self.client_button.setVisible(False)
        self.ip_address_label = QLabel("Your address is xxx.xxx.xxx.xxx", self)
        self.ip_address_label.setFont(QFont("Arial", 50))
        self.ip_address_label.move(50, 50)
        self.ip_address_label.setVisible(True)

        self.port_label = QLabel("You are listining on port xxxx", self)
        self.port_label.setFont(QFont("Arial", 50))
        self.port_label.move(50, 200)
        self.port_label.setVisible(True)

        self.status_label = QLabel("Waiting for connection...", self)
        self.status_label.setFont(QFont("Arial", 50))
        self.status_label.move(50, 400)
        self.status_label.setVisible(True)
        self.server = Server(self)
        ip_local, ip_ham, ip_port = self.server.find_ip()
        if ip_local == "0.0.0.0":
            print("Nie znaleziono polaczenia sieciowego. Sprawdz...")
            return
        else:
            if ip_ham == "0.0.0.0":
                self.ip_address_label.setText("Your address is {0}".format(ip_local))
            else:
                self.ip_address_label.setText("Your address is {0}".format(ip_ham))
        self.port_label.setText("You are listining on port {0}".format(ip_port))
        self.isServer = True
        self.server.start()

    def start_connection(self):
        try:
            addr = self.ip_address_field.toPlainText()
            port = int(self.port_field.toPlainText())
        except:
            return
        self.isServer = False
        self.client = Client(addr, port, self)
        self.client.start()
        
    def connected_with_player(self):
        if DEBUG:
            self.client = Client("127.0.0.1", 10000, self)
        if self.isServer:
            if random.random() < 0.5:
                self.turn_states(0)
            else:
                self.send_message(1)
        self.clear_window()
        self.init_game()
        self.draw_screen()
        
    def clear_window(self):
        self.ip_address_field.setVisible(False)
        self.ip_address_label.setVisible(False)
        self.port_field.setVisible(False)
        self.port_label.setVisible(False)
        self.ok_button.setVisible(False)
        self.view.setVisible(True)
        self.preview.setVisible(True)

    def init_game(self):
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
        self.opp_mana = [[0, True]]
        self.opp_hand = [-1, -1, -1, -1, -1]
        self.opp_bfield = [-1, -1, -1, -1, -1, -1]
        self.opp_graveyard = []
        self.change_button_state = True

    def startTime(self):
        """
        zablokuj wybieranie kart na 20ms po kliknięciu
        zawsze wybiera pierwszą kartę na wierzchu
        """
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(20)
        self.timer.start()
        self.timer.timeout.connect(self.change_state)

    def change_state(self):
        # ZAWSZE WYBIERA JEDNĄ KARTĘ
        self.locked = False
        
    def draw_screen(self):
        self.background = QGraphicsPixmapItem(QPixmap("res//img//background.png"))
        self.view_scene.addItem(self.background)
        self.preview_scene.addItem(QGraphicsPixmapItem(QPixmap("res//img//console.png")))
        for i in range(len(self.opp_shields)):
            if self.opp_shields[i]:
                card = CardView("op_sh", i + 1, self)
                transform = QTransform().rotate(180)
                pixmap = QPixmap("res//img//cardback.png").transformed(transform)
                card.setPixmap(pixmap)
                card.setPos(74, 139 + i * 125)  # tarcze przeciwnika
                self.view_scene.addItem(card)

        for i in range(len(self.shields)):
            if not self.shields[i][0] == -1:
                card = CardView("yu_sh", i + 1, self)
                if self.shields[i][1]:
                    card.setPixmap(QPixmap("res//img//cardback.png"))
                else:
                    item = self.find_card(self.shields[i][0])
                    card.set_card(item)
                    card.setPixmap(QPixmap(item.image))
                card.setPos(866, 14 + i * 125)  # tarcze twoje
                self.view_scene.addItem(card)
                
        for i in range(len(self.bfield)):
            if not self.bfield[i] == -1:
                card = CardView("yu_bf", i + 1, self)
                item = self.find_card(self.bfield[i])
                card.set_card(item)
                card.setPixmap(QPixmap(item.image))
                card.setPos(232 + i * 95, 389)  # pole potworów twoje
                self.view_scene.addItem(card)
                
        for i in range(len(self.opp_bfield)):
            if not self.opp_bfield[i] == -1:
                card = CardView("op_bf", i + 1, self)
                item = self.find_card(self.opp_bfield[i])
                card.set_card(item)
                card.setPixmap(QPixmap(item.image))
                card.setPos(232 + i * 95, 264)  # pole potworów przeciwnika
                self.view_scene.addItem(card)
                
        if not len(self.opp_graveyard) == 0:      
            card = CardView("op_gv", 1, self)
            item = self.find_card(self.opp_graveyard[len(self.opp_graveyard) - 1])
            card.set_card(item)
            transform = QTransform().rotate(180)
            card.setPixmap(QPixmap(item.image).transformed(transform))
            card.setPos(74, 14) # cmentarz przeciwnika
            self.view_scene.addItem(card)

        if not len(self.graveyard) == 0:      
            card = CardView("yu_gv", 1, self)
            item = self.find_card(self.graveyard[len(self.graveyard) - 1])
            card.set_card(item)
            card.setPixmap(QPixmap(item.image))
            card.setPos(866, 639) # twój cmentarz
            self.view_scene.addItem(card)
            
        # twoje karty w ręku
        self.add_cards_to_scene(self.hand, "yu_hd")

        # karty w ręce przeciwnika
        self.add_cards_to_scene(self.opp_hand, "op_hd")

        # twoja mana
        self.add_mana_to_scene(self.mana, "yu_mn")

        # mana przeciwnika
        self.add_mana_to_scene(self.opp_mana, "op_mn")

        # rozszerz logi
        self.extend_logs_button = QPushButton()
        self.extend_logs_button.setFixedSize(10, 10)
        self.extend_logs_button.clicked.connect(self.change_logs_size)
        proxy = self.preview_scene.addWidget(self.extend_logs_button)
        if self.change_button_state:
            self.extend_logs_button.setText("+")
            proxy.setPos(20, 200)
        else:
            self.extend_logs_button.setText("-")
            proxy.setPos(20, 20)

        print("debug")

        #logi
        if not len(self.logs) == 0:
            if self.change_button_state:
                lenght = min(len(self.logs), 3)
            else:
                lenght = min(len(self.logs), 10)
            x_pos = 20
            y_pos = 698
            y_height = 50
            x_width = 296
            for i in range(lenght):
                log = self.logs[i]
                ramka = QGraphicsRectItem(x_pos, y_pos, x_width, y_height)
                ramka.setPen(QPen(QColor(255, 0, 0)))
                self.preview_scene.addItem(ramka)

                tekst = QGraphicsTextItem(log.info)
                tekst.setPos(x_pos + 10, y_pos + 5)
                tekst.setTextWidth(x_width-20)
                self.preview_scene.addItem(tekst)
                y_pos -= 60
        print("debug2")
        
    def card_clicked(self, x, y, c_id=None):
        self.refresh_screen()
        # self.preview_scene.removeItem(self.card_prev)
        if not self.change_button_state:
            if c_id is not None:
                self.draw_preview_card(c_id)
        print("debug3")
        self.highlightCard(x, x + 85, y, y + 115, QColor(255, 0, 0))

    def change_logs_size(self):
        self.change_button_state = not self.change_button_state
        self.refresh_screen()
        
    def highlightCard(self, x1, x2, y1, y2, color):
        """
        draw a frame around a clicked card on the board
        """
        self.view_scene.addLine(x1 - 1, y1 - 1, x1 - 1, y2 + 1, QPen(color))
        self.view_scene.addLine(x2 + 1, y1 - 1, x2 + 1, y2 + 1, QPen(color))
        self.view_scene.addLine(x1 - 1, y1 - 1, x2 + 1, y1 - 1, QPen(color))
        self.view_scene.addLine(x1 - 1, y2 + 1, x2 + 1, y2 + 1, QPen(color))

    def draw_preview_card(self, card_id):
        """
        draw a preview of the clicked card on preview side of the screen
        """
        self.card_prev = QGraphicsPixmapItem(QPixmap(self.find_card(card_id).info))
        self.card_prev.setPos(0, 0)
        self.preview_scene.addItem(self.card_prev)
        
    def add_cards_to_scene(self, arr, type):
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
            else:
                card = self.find_card(arr[i])
                item.set_card(card)
                link = card.image
            pixmap = QPixmap(link)
            if type == "op_hd":
                transform = QTransform().rotate(180)
                pixmap = pixmap.transformed(transform)
            item.setPixmap(pixmap)
            if size <= 6:
                if size % 2 == 0:
                    item.setPos(422 - 95 * (size/2 - 1) + i * 95, height)
                else:
                    item.setPos(512 - 85 / 2 - 95 * ((size - 1) / 2) + 95 * i, height)
            else:
                item.setPos(232 + (475 / (size - 1)) * i, height)
            self.view_scene.addItem(item)
            
    def add_mana_to_scene(self, arr, type):
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
            pixmap = QPixmap(card.image)
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
                    item.setPos(422 - 95 * (size/2 - 1) + i * 95, height)
                else:
                    item.setPos(512 - 85 / 2 - 95 * ((size - 1) / 2) + 95 * i, height)
            else:
                item.setPos(232 + (475 / (size - 1)) * i, height)
            self.view_scene.addItem(item)
            
    def find_card(self, iden):
        for card in self.cardlist:
            if card.id == iden:
                return card

    def send_message(self, *msg):
        """
        Wiadomości wysyłane do przeciwnika
        0 - przeciwnik wygrał
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
        if self.isServer:
            self.server.send_data(msg)
        else:
            self.client.send_data(msg)
        
    def turn_states(self, state):
        """
        0 -> pierwsza runda w grze
        1 -> dobierz kartę + rzucanie many/czary/creatury
        """
        if state == 0:
            self.card_to_draw = 0
            self.card_to_mana = 1
            self.your_turn = True
        elif state == 1:
            self.card_to_draw = 1
            self.card_to_mana = 1
            self.your_turn = True

    def win(self):
        print("Winner!")

    def refresh_screen(self):
        self.view_scene.clear()
        self.preview_scene.clear()
        self.draw_screen()

    def add_log(self, text):
        self.logs.appendleft(LogInfo(text))
        self.refresh_screen()

#   METODY MENU
#####################################################

    def m_draw_a_card(self):
        ##########################
        for i in range(10):
            self.add_log("Test")
        ##########################
        if self.card_to_draw > 0:
            if not len(self.deck) == 0:
                card = self.deck.pop(0)
                self.hand.append(card)
                #self.send_message(3)
            else:
                print("Przegrales")
                #self.send_message(0)
            self.refresh_screen()
        
    def m_end_turn(self):
        self.send_message(2)
        self.your_turn = False
        
    def m_summon_card(self, iden):
        card = self.find_card(self.hand[iden - 1])
        sum = 0
        for item in self.weights:
            sum += item
        if sum >= int(card.cost) and not self.weights[self.dict_civ[card.civ]] == 0:
            if card.typ == "Creature":
                for i in range(len(self.bfield) - 1):
                    if self.bfield[i] == -1:
                        card = self.hand.pop(iden - 1)
                        self.bfield[i] = card
                        self.send_message(4, card, i)
                        break
            elif card.typ == "Spell":
                if self.bfield[5] == -1:
                    card = self.hand.pop(iden - 1)
                    self.bfield[5] = card
                    self.send_message(4, card, 5)
        else:
            print("Za mało many")
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
        if self.card_to_mana > 0:
            card = self.hand.pop(iden-1)
            self.mana.append([card, True])
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