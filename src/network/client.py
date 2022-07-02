from PySide6.QtCore import QIODevice, QDataStream, QByteArray, Signal
from PySide6.QtNetwork import QTcpSocket, QHostAddress, QAbstractSocket

import logging


class Client(QTcpSocket):
    """
    Client class for communication Client <-> Server.
    """
    messageReceived = Signal(str)
    def __init__(self, address, port, parent=None):
        """
        :param address: Address of the server
        :param port: Port to connect to
        """
        super(Client, self).__init__()
        self.address = address
        self.port = port
        self.parent = parent
        self.errorOccurred.connect(self.error_handle)
        self.readyRead.connect(self.receive_data)
        self.disconnected.connect(self.disconnected_with_server)

        self.log = logging.getLogger("client")

    def start_connection(self):
        self.log.debug(f"Starting a connection to {self.address}:{self.port}")
        if type(self.port) == str:
            self.port = int(self.port)
        self.connectToHost(QHostAddress(self.address), self.port, QIODevice.ReadWrite)
        self.log.debug(f"Validate connection")
        if not self.waitForConnected(10000):
            self.log.error(f"Couldn't create a valid connection to host {self.address}:{self.port}.")
            self.abort()

    def send_data(self, data):
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
        self.write(block)
        self.log.debug(f"Sent to opponent data: {msg}")

    def receive_data(self):
        stream = QDataStream(self)
        stream.setVersion(QDataStream.Qt_5_15)
        # Make sure all data was processed
        while self.bytesAvailable() > 0:
            data = stream.readString()
            msg = str(data)
            self.log.debug(f"Received from opponent data: {msg}")
            self.messageReceived.emit(msg)

    def error_handle(self, error):
        # TODO: custom handling of the error
        self.log.debug(f"{self.error()}: {self.errorString()}")
        # if error == QAbstractSocket.RemoteHostClosedError:
        #     self.log.debug(f"QAbstractSocket.RemoteHostClosedError: {self.errorString()}")
        #     self.log.error("Opponent closed the connection.")
        self.log.error(f"Error happened with connection to the opponent. Reason: {self.errorString()}")
        self.abort()

    def disconnected_with_server(self):
        self.log.error("The connection was closed with the opponent.")
        self.abort()

    def run(self):
        self.start_connection()
