from PyQt5.QtNetwork import QTcpSocket, QTcpServer, QHostAddress, QNetworkInterface, QAbstractSocket
from PyQt5.QtCore import QThread, QIODevice, QDataStream, QByteArray
import re


class Client(QThread):
    def __init__(self, address, port, parent=None):
        super(Client, self).__init__()
        self.address = address
        self.port = port
        self.parent = parent
        self.socket = QTcpSocket()
        self.socket.connected.connect(self.parent.connected_with_player)
        # self.socket.disconnected.connect()
        self.socket.error.connect(self.server_error_handle)
        # self.socket.bytesWritten.connect()
        self.socket.readyRead.connect(self.receive_data)
        
    def connect(self):
        self.socket.connectToHost(QHostAddress(self.address), self.port, QIODevice.ReadWrite)
        self.socket.waitForConnected(10000)
        
    def send_data(self, data):
        # self.socket.write
        block = QByteArray()
        stream = QDataStream(block, QIODevice.ReadWrite)
        stream.setVersion(QDataStream.Qt_5_8)
        msg = bytes(data, encoding='ascii')
        stream.writeString(msg)
        stream.device().seek(0)
        
    def receive_data(self):
        stream = QDataStream(self.socket)
        stream.setVersion(QDataStream.Qt_5_8)
        if self.socket.bytesAvailable() < 2:
            return
        data = stream.readUInt16()
        if self.socket.bytesAvailable() < data:
            return
        print(str(data.readString(), encoding='ascii'))

    def server_error_handle(self, error):
        if error == QAbstractSocket.RemoteHostClosedError:
            print("QAbstractSocket.RemoteHostClosedError")
        else:
            print("Error occured: {}".format(self.socket.errorString()))
        
    def __del__(self):
        self.wait()
        
    def run(self):
        self.connect()


class Server(QThread):
    def __init__(self, parent=None):
        super(Server, self).__init__()
        self.parent = parent
        self.server = QTcpServer()
        self.server.newConnection.connect(self.conn_handle)
        self.server.acceptError.connect(self.server_error_handle)
        self.connected = False
        self.ham_addr = "0.0.0.0"
        self.wifi_addr = "0.0.0.0"
        self.port = 10023

    def find_ip(self):
        ham_pat = r"^25\.[1-2]?[0-9]?[0-9]\.[1-2]?[0-9]?[0-9]\.[1-2]?[0-9]?[0-9]$"
        wifi_pat = r"^192\.168\.[1-2]?[0-9]?[0-9]\.[1-2]?[0-9]?[0-9]$"
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
        self.socket.readyRead.connect(self.receive_data)
        self.socket.acceptError.connect(self.socket_error_handle)
        self.parent.connected_with_player()

    def server_error_handle(self):
        print("Jakiś error")

    def socket_error_handle(self):
        print("Jakis inny error")

    def __del__(self):
        self.wait()

    def run(self):
        if self.ham_addr == "0.0.0.0":
            self.server.listen(QHostAddress(self.wifi_addr), self.port)
        else:
            self.server.listen(QHostAddress(self.ham_addr), self.port)
        self.server.waitForNewConnection(100000)

    def send_data(self, data):
        block = QByteArray()
        stream = QDataStream(block, QIODevice.ReadWrite)
        stream.setVersion(QDataStream.Qt_5_8)
        msg = bytes(data, encoding='ascii')
        stream.writeString(msg)
        stream.device().seek(0)

    def receive_data(self):
        stream = QDataStream(self.socket)
        stream.setVersion(QDataStream.Qt_5_8)
        if self.socket.bytesAvailable() < 2:
            return
        data = stream.readUInt16()
        if self.socket.bytesAvailable() < data:
            return
        msg = str(data.readString(), encoding='ascii')
        self.parent.received_message(msg)
