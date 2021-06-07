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
        # self.bytesWritten.connect()

    def setup_logger(self):
        self.log = logging.getLogger("dm_game")
        self.log.setLevel(logging.DEBUG)

    def start_connection(self):
        print("START_CONNECTION")
        if type(self.port) == str:
            self.port = int(self.port)
        self.connectToHost(QHostAddress(self.address), self.port, QIODevice.ReadWrite)
        print("WAIT_FOR_CONNECTED")
        if not self.waitForConnected(10000):
            print("Critical error, do nothing")

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
        self.write(block)
        print("SENT: " + msg)

    def receive_data(self):
        print("RECEIVE")
        stream = QDataStream(self)
        stream.setVersion(QDataStream.Qt_5_15)
        if self.bytesAvailable() < 2:
            return
        data = stream.readString()
        # if self.bytesAvailable() < data:
        #     return
        msg = str(data)
        print("RECEIVED: " + msg)
        self.messageReceived.emit(msg)

    def server_error_handle(self, error):
        print("ERROR")
        if error == QAbstractSocket.RemoteHostClosedError:
            print("QAbstractSocket.RemoteHostClosedError")
        else:
            print("Error occured: {}".format(self.errorString()))

    def disconnected_with_server(self):
        print("DISCONNECTED")

    # def __del__(self):
    #     self.wait()

    def run(self):
        self.start_connection()
