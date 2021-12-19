import sys
sys.path.insert(0, "D:\Projects\DuelMasters-game\src")
from PySide6.QtWidgets import QApplication, QLineEdit, QPushButton, QWidget

from src.network.client import Client

class ChatClient(QWidget):
    def __init__(self):
        super(ChatClient, self).__init__()

        self.resize(800, 600)

        self.line_edit = QLineEdit(self)
        self.line_edit.move(0, 0)

        self.send_button = QPushButton("Send", self)
        self.send_button.clicked.connect(self.send)
        self.send_button.move(0, 400)

        self.client = Client("192.168.56.101", 10023)
        self.client.run()

    def send(self):
        data = self.line_edit.text()
        self.client.send_data(data)
        self.line_edit.setText("")
    

if __name__ == "__main__":
    app = QApplication(sys.argv[:1])
    window = ChatClient()
    window.show()
    sys.exit(app.exec_())

