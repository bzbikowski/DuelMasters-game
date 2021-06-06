from PySide2.QtCore import QIODevice, QDataStream, QByteArray
from PySide2.QtNetwork import QTcpSocket, QHostAddress, QAbstractSocket

from src.controller import Controller


class Client(QTcpSocket):
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
        self.connected.connect(self.parent.connected_with_player)
        self.error.connect(self.server_error_handle)
        self.readyRead.connect(self.receive_data)
        self.disconnected.connect(self.disconnected)
        # self.bytesWritten.connect()

    def start_connection(self):
        print("START_CONNECTION")
        self.connectToHost(QHostAddress(self.address), self.port, QIODevice.ReadWrite)
        self.waitForConnected(10000)

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
        # msg = bytes(msg, encoding='ascii')
        stream.writeString(msg)
        stream.device().seek(0)
        print("SENT: " + msg)

    def receive_data(self):
        print("RECEIVE")
        stream = QDataStream(self)
        stream.setVersion(QDataStream.Qt_5_15)
        if self.bytesAvailable() < 2:
            return
        data = stream.readUInt16()
        if self.bytesAvailable() < data:
            return
        msg = str(data.readString(), encoding='ascii')
        print("RECEIVED: " + msg)
        self.controller.received_message(msg)

    def server_error_handle(self, error):
        print("ERROR")
        if error == QAbstractSocket.RemoteHostClosedError:
            print("QAbstractSocket.RemoteHostClosedError")
        else:
            print("Error occured: {}".format(self.errorString()))

    def disconnected(self):
        print("DISCONNECTED")

    # def __del__(self):
    #     self.wait()

    def run(self):
        self.start_connection()
