from PySide2.QtNetwork import QTcpSocket, QTcpServer, QHostAddress, QNetworkInterface, QAbstractSocket
from PySide2.QtCore import QThread, QIODevice, QDataStream, QByteArray
import sys

msg = "*beep*"

data = ""

def receive_data():
    print(socket.readAll())
    #stream.startTransaction()
    #data += stream.readString()
    #print("PARTIAL: " + data)
    #if not stream.commitTransaction():
    #    return
    #print("FINAL: " + data)

def disconnected():
    print("DISC")
    sys.exit(1)

def error_handle(err):
    print(err)
    sys.exit(1)

if __name__ == "__main__":
    socket = QTcpSocket() 
    socket.readyRead.connect(receive_data)
    socket.disconnected.connect(disconnected)
    socket.errorOccurred.connect(error_handle)
    stream = QDataStream(socket)
    stream.setVersion(QDataStream.Qt_5_10)
    socket.connectToHost(QHostAddress("192.168.56.101"), 10099, QIODevice.ReadWrite)
    if socket.waitForConnected(100000):
        while True:
            pass