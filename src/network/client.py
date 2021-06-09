from PySide2.QtCore import QIODevice, QDataStream, QByteArray, Signal
from PySide2.QtNetwork import QTcpSocket, QHostAddress, QAbstractSocket

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
        self.log = None
        self.address = address
        self.port = port
        self.parent = parent
        self.error.connect(self.server_error_handle)
        self.readyRead.connect(self.receive_data)
        self.disconnected.connect(self.disconnected_with_server)
        self.setup_logger()

    def setup_logger(self):
        self.log = logging.getLogger("dm_game")
        self.log.setLevel(logging.DEBUG)

    def start_connection(self):
        self.log.debug(f"Starting a connection to {self.address}:{self.port}")
        if type(self.port) == str:
            self.port = int(self.port)
        self.connectToHost(QHostAddress(self.address), self.port, QIODevice.ReadWrite)
        self.log.debug(f"Validate connection")
        if not self.waitForConnected(10000):
            self.log.error(f"Couldn't create a valid connection to host {self.address}:{self.port}. Exiting...")
            self.close()

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
        if self.bytesAvailable() < 2:
            return
        data = stream.readString()
        msg = str(data)
        self.log.debug(f"Received from opponent data: {msg}")
        self.messageReceived.emit(msg)

    def server_error_handle(self, error):
        if error == QAbstractSocket.RemoteHostClosedError:
            self.log.debug(f"QAbstractSocket.RemoteHostClosedError: {self.errorString()}")
            self.log.error("Opponent closed the connection. Exiting...")
        else:
            self.log.debug(self.errorString())
            self.log.error("Unknown error happened with connection. Exiting...")
        self.close()

    def disconnected_with_server(self):
        self.log.error("The connection was closed with the opponent. Exiting...")
        self.close()

    def run(self):
        self.start_connection()
