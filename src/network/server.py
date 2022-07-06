import re

from PySide6.QtCore import QIODevice, QDataStream, QByteArray, Signal
from PySide6.QtNetwork import QTcpServer, QHostAddress, QNetworkInterface

import logging


class Server(QTcpServer):
    """
    Server class for communication Client <-> Server.
    """
    connectionOk = Signal(None)
    messageReceived = Signal(str)
    clientError = Signal(None)
    def __init__(self, parent=None):
        super(Server, self).__init__()
        self.parent = parent
        self.socket = None
        self.setMaxPendingConnections(2)
        self.newConnection.connect(self.conn_handle)
        self.acceptError.connect(self.server_error_handle)
        self.connected = False
        self.port = 10023 # TODO: make it configurable?

        self.log = logging.getLogger("client")

    def conn_handle(self):
        self.log.info("Found new connection")
        self.socket = self.nextPendingConnection()
        client_ip_address = self.socket.localAddress().toString()
        client_port = self.socket.localPort()
        self.log.debug(f"Client IP address and port: {client_ip_address}:{client_port}")
        if not self.socket.waitForConnected(10000):
            self.log.error(f"Couldn't create a valid connection with host {client_ip_address}:{client_port}.")
            self.close_connection()
        self.socket.readyRead.connect(self.receive_data)
        self.socket.errorOccurred.connect(self.socket_error_handle)
        self.socket.disconnected.connect(self.client_disconnected)
        self.log.info("Connection OK")
        self.connectionOk.emit()

    def server_error_handle(self, error):
        self.log.error(f"Server error: {self.errorString()}")
        self.close_connection()

    def socket_error_handle(self, error):
        # TODO: custom handling of the error
        try:
            print(str(error))
        except:
            pass
        self.log.debug(f"{self.socket.error()}: {self.socket.errorString()}")
        self.log.error(f"Error happened with connection to the opponent. Reason: {self.socket.errorString()}")

    def client_disconnected(self):
        self.log.error("The connection was closed with the opponent.")
        self.close_connection()

    def close_connection(self):
        try:
            self.socket.disconnectFromHost()
        except AttributeError as e:
            pass
        self.clientError.emit()
        self.close()

    def run(self):
        self.log.info(f"Looking for connection on port {self.port}")
        self.listen(QHostAddress.AnyIPv4, self.port)

    def send_data(self, data):
        msg = ""
        for item in data:
            m = hex(int(item))[2:]
            while len(m) < 8:
                m = "0" + m
            msg += m
        block = QByteArray()
        stream = QDataStream(block, QIODevice.WriteOnly)
        stream.setVersion(QDataStream.Qt_5_15)
        stream.writeString(msg)
        stream.device().seek(0)
        self.socket.write(block)
        self.log.debug(f"Sent to opponent data: {msg}")

    def receive_data(self):
        stream = QDataStream(self.socket)
        stream.setVersion(QDataStream.Qt_5_15)
        # Make sure all data was processed
        while self.socket.bytesAvailable() > 0:
            data = stream.readString()
            msg = str(data)
            self.log.debug(f"Received from opponent data: {msg}")
            self.messageReceived.emit(msg)
        
