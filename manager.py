from PyQt5.QtWidgets import QWidget, QPushButton


class DeckManager(QWidget):
    def __init__(self, parent=None):
        super(DeckManager, self).__init__()
        width = 400
        height = 400
        self.setFixedSize(width, height)
        self.parent = parent
        self.button = QPushButton("Push", self)
        self.button.clicked.connect(self.clicked)
        self.parent.deck = [(i % 5) + 1 for i in range(40)]

    def clicked(self):
        print("Clikced")