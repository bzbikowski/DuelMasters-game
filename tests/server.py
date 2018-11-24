from PyQt5.QtNetwork import QTcpSocket, QTcpServer, QHostAddress, QNetworkInterface, QAbstractSocket
from PyQt5.QtCore import QThread, QIODevice, QDataStream, QByteArray

msg = "*beep*"

if __name__ == "__main__":
    server = QTcpServer()
    server.setMaxPendingConnections(2)
    server.listen(QHostAddress("192.168.10.44"), 10023)
    if server.waitForNewConnection(100000):
        socket = server.nextPendingConnection()
        block = QByteArray()
        stream = QDataStream(block, QIODevice.WriteOnly)
        stream.setVersion(QDataStream.Qt_5_10)
        msg = bytes(msg, encoding='ascii')
        stream.writeString(msg)
        stream.device().seek(0)
