import sys
from PySide2.QtWidgets import QApplication, QTextEdit, QWidget
from src.network.server import Server

class ChatServer(QWidget):
    def __init__(self):
        super(ChatServer, self).__init__()

        self.chat_feed = QTextEdit(self)

        self.server = Server()
        self.server.messageReceived.connect(self.handle_message)
        self.server.run()

    def handle_message(self, msg):
        self.chat_feed.setText(self.chat_feed.toPlainText() + msg)
    

if __name__ == "__main__":
    app = QApplication(sys.argv[:1])
    window = ChatServer()
    window.show()
    sys.exit(app.exec_())

