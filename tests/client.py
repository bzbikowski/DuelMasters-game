from PySide2.QtNetwork import QTcpSocket, QTcpServer, QHostAddress, QNetworkInterface, QAbstractSocket
from PySide2.QtCore import QThread, QIODevice, QDataStream, QByteArray

msg = "*beep*"

if __name__ == "__main__":
    socket = QTcpSocket()
    socket.connectToHost(QHostAddress("192.168.10.44"), 10023, QIODevice.ReadWrite)
    if socket.waitForConnected(100000):
        while True:
            stream = QDataStream(socket)
            stream.setVersion(QDataStream.Qt_5_10)
            if socket.bytesAvailable() < 2:
                pass
            data = stream.readUInt16()
            if socket.bytesAvailable() < data:
                pass
            msg = str(data.readString(), encoding='ascii')
            print(msg)
