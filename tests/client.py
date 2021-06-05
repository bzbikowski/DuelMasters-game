from PySide2.QtNetwork import QTcpSocket, QTcpServer, QHostAddress, QNetworkInterface, QAbstractSocket
from PySide2.QtCore import QThread, QIODevice, QDataStream, QByteArray

msg = "*beep*"

stream = QDataStream(socket)
stream.setVersion(QDataStream.Qt_5_10)
data = ""

if __name__ == "__main__":
    socket = QTcpSocket()
    socket.connectToHost(QHostAddress("192.168.56.101"), 10099, QIODevice.ReadWrite)
    socket.readyRead.connect(receive_data)

    if socket.waitForConnected(100000):
        while True:
            stream.startTransaction()
            data = stream.readString()
            if not stream.commitTransaction():
                continue
            print(data)

def receive_data():
    stream.startTransaction()
    data += stream.readString()
    if not stream.commitTransaction():
        return
    print(data)
