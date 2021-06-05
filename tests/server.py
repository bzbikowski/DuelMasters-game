from PySide2.QtCore import QIODevice, QDataStream, QByteArray
from PySide2.QtNetwork import QTcpServer, QHostAddress

msg = "*beep*"

if __name__ == "__main__":
    server = QTcpServer()
    server.setMaxPendingConnections(2)
    server.listen(QHostAddress("192.168.10.44"), 10099)
    if server.waitForNewConnection(100000):
        socket = server.nextPendingConnection()
        print("Znaleziono cos")
        block = QByteArray()
        stream = QDataStream(block, QIODevice.WriteOnly)
        stream.setVersion(QDataStream.Qt_5_10)
        msg = bytes(msg, encoding='ascii')
        stream.writeString(msg)
        stream.device().seek(0)
