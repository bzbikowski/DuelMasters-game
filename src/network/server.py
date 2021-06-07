import re

from PySide2.QtCore import QIODevice, QDataStream, QByteArray, Signal
from PySide2.QtNetwork import QTcpServer, QHostAddress, QNetworkInterface


class Server(QTcpServer):
    """
    Server class for communication Client <-> Server.
    """
    connectionOk = Signal(None)
    messageReceived = Signal(str)
    def __init__(self, parent=None):
        super(Server, self).__init__()
        self.parent = parent
        self.socket = None
        self.setMaxPendingConnections(2)
        self.newConnection.connect(self.conn_handle)
        self.acceptError.connect(self.server_error_handle)
        self.connected = False
        self.wifi_addr = "0.0.0.0"
        self.port = 10023

    def find_ip(self):
        wifi_pat = r"^192\.168\.[0-2]?[0-9]?[0-9]\.[0-2]?[0-9]?[0-9]$" # Only for debbuging
        inet = QNetworkInterface().interfaceFromName("eth0")
        addresses = inet.allAddresses()
        print("Found interfaces: " + str(addresses))
        for addr in addresses:
            addr_str = addr.toString()
            if re.match(wifi_pat, addr_str):
                self.wifi_addr = addr_str
        return self.wifi_addr, self.port

    def conn_handle(self):
        print("NEW_CONNECTION")
        self.socket = self.nextPendingConnection()
        print("SOCKET_READY")
        if not self.socket.waitForConnected(10000):
            print("Critical error, do nothing")
        self.socket.readyRead.connect(self.receive_data)
        self.socket.error.connect(self.socket_error_handle)
        self.socket.disconnected.connect(self.client_disconnected)
        print("CONNECTION_OK")
        self.connectionOk.emit()

    def server_error_handle(self):
        print("ERROR: server_error_handle")

    def socket_error_handle(self):
        print("ERROR: socket_error_handle")

    def client_disconnected(self):
        print("ERROR: client_disconnected")

    # def __del__(self):
    #     self.close()

    def run(self):
        print("LOOKING_FOR_CONNECTION")
        self.listen(QHostAddress(self.wifi_addr), self.port)

    def send_data(self, data):
        print("SENT")
        msg = ""
        for item in data:
            m = hex(int(item))[2:]
            while len(m) < 2:
                m = "0" + m
            msg += m
        block = QByteArray()
        stream = QDataStream(block, QIODevice.WriteOnly)
        stream.setVersion(QDataStream.Qt_5_15)
        stream.writeString(msg)
        stream.device().seek(0)
        self.socket.write(block)
        print("SENT: " + msg)

    def receive_data(self):
        print("RECEIVE")
        stream = QDataStream(self.socket)
        stream.setVersion(QDataStream.Qt_5_15)
        if self.socket.bytesAvailable() < 2:
            return
        data = stream.readString()
        # if self.socket.bytesAvailable() < len(data):
        #     return
        msg = str(data)
        print("RECEIVED: " + msg)
        self.messageReceived.emit(msg)
