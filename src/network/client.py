from PySide2.QtCore import QThread, QIODevice, QDataStream, QByteArray
from PySide2.QtNetwork import QTcpSocket, QHostAddress, QAbstractSocket

from src.controller import Controller


class Client(QThread):
    """
    Client class for communication Client <-> Server.
    """

    def __init__(self, address, port, parent=None):
        """
        :param address: Address of the server
        :param port: Port to connect to
        """
        super(Client, self).__init__()
        self.address = address
        self.port = port
        self.parent = parent
        self.controller = Controller(parent)
        self.socket = QTcpSocket()
        self.socket.connected.connect(self.parent.connected_with_player)
        self.socket.error.connect(self.server_error_handle)
        self.socket.readyRead.connect(self.receive_data)
        self.socket.disconnected.connect(self.disconnected)
        # self.socket.bytesWritten.connect()

    def start_connection(self):
        self.socket.connectToHost(QHostAddress(self.address), self.port, QIODevice.ReadWrite)
        self.socket.waitForConnected(10000)

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
        # msg = bytes(msg, encoding='ascii')
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

    def server_error_handle(self, error):
        if error == QAbstractSocket.RemoteHostClosedError:
            print("QAbstractSocket.RemoteHostClosedError")
        else:
            print("Error occured: {}".format(self.socket.errorString()))

    def disconnected(self):
        print("disconected")

    def __del__(self):
        self.wait()

    def run(self):
        self.start_connection()
