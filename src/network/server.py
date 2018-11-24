from PyQt5.QtNetwork import QTcpSocket, QTcpServer, QHostAddress, QNetworkInterface, QAbstractSocket
from PyQt5.QtCore import QThread, QIODevice, QDataStream, QByteArray
from src.controller import Controller
import re


class Server(QThread):
    """
    Server class for communication Client <-> Server.
    """
    def __init__(self, parent=None):
        super(Server, self).__init__()
        self.parent = parent
        self.socket = None
        self.controller = Controller(parent)
        self.server = QTcpServer()
        self.server.setMaxPendingConnections(2)
        self.server.newConnection.connect(self.conn_handle)
        self.server.acceptError.connect(self.server_error_handle)
        self.connected = False
        self.ham_addr = "0.0.0.0"
        self.wifi_addr = "0.0.0.0"
        self.port = 10023

    def find_ip(self):
        ham_pat = r"^25\.[1-2]?[0-9]?[0-9]\.[1-2]?[0-9]?[0-9]\.[1-2]?[0-9]?[0-9]$"
        wifi_pat = r"^192\.168\.[0-2]?[0-9]?[0-9]\.[0-2]?[0-9]?[0-9]$"
        inet = QNetworkInterface().interfaceFromName("eth0")
        addr = inet.allAddresses()
        for add in addr:
            add_str = add.toString()
            if re.match(ham_pat, add_str):
                self.ham_addr = add_str
            elif re.match(wifi_pat, add_str):
                self.wifi_addr = add_str
        return self.wifi_addr, self.ham_addr, self.port

    def conn_handle(self):
        self.socket = self.server.nextPendingConnection()
        if not self.socket.isValid():
            print("Critical error, do nothing")
        self.socket.readyRead.connect(self.receive_data)
        self.socket.acceptError.connect(self.socket_error_handle)
        # self.socket.disconnected.connect(self.disconnected)
        # self.socket.bytesWritten.connect()
        self.parent.connected_with_player()

    def server_error_handle(self):
        print("Jakiś error")

    def socket_error_handle(self):
        print("Jakis inny error")

    def __del__(self):
        self.server.close()
        self.wait()

    def run(self):
        if self.ham_addr == "0.0.0.0":
            self.server.listen(QHostAddress(self.wifi_addr), self.port)
        else:
            self.server.listen(QHostAddress(self.ham_addr), self.port)

    def send_data(self, data):
        msg = ""
        for item in data:
            m = hex(int(item))[2:]
            while len(m) < 2:
                m = "0" + m
            msg += m
        print(msg)
        block = QByteArray()
        stream = QDataStream(block, QIODevice.WriteOnly)
        stream.setVersion(QDataStream.Qt_5_10)
        msg = bytes(msg, encoding='ascii')
        stream.writeString(msg)
        stream.device().seek(0)

    def receive_data(self):
        stream = QDataStream(self.socket)
        stream.setVersion(QDataStream.Qt_5_10)
        if self.socket.bytesAvailable() < 2:
            return
        data = stream.readUInt16()
        if self.socket.bytesAvailable() < data:
            return
        msg = str(data.readString(), encoding='ascii')
        print(msg)
        self.controller.received_message(msg)
