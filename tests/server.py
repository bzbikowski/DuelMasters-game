from PySide2.QtCore import QIODevice, QDataStream, QByteArray
from PySide2.QtNetwork import QTcpServer, QHostAddress
import time

msg = "*beep*"

if __name__ == "__main__":
    server = QTcpServer()
    server.setMaxPendingConnections(2)
    server.listen(QHostAddress("192.168.56.101"), 10099)
    if server.waitForNewConnection(100000):
        print("NEW HOST")
        socket = server.nextPendingConnection()
        while True:
            block = QByteArray()
            stream = QDataStream(block, QIODevice.WriteOnly)
            stream.setVersion(QDataStream.Qt_5_10)
            stream.writeString(msg)
            stream.device().seek(0)
            socket.write(block)
            print("PING")
            time.sleep(10)
        socket.disconnectFromHost()
