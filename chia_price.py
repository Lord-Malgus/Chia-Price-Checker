from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QHBoxLayout, QWidget
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QFont, QPainter
import sys
import requests

class TitleBar(QMainWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setWindowFlags(Qt.FramelessWindowHint)

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint (event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

class PriceMonitor(TitleBar):
    def __init__(self):
        super().__init__()        
        self.resize(190, 80)
        self.move(QApplication.desktop().screen().rect().center()- self.rect().center())
        self.title_label = QLabel("Dexie Chia Price", self)
        self.title_label.setFont(QFont("Helvetica", 9))
        self.title_label.move (20,-5)
        self.price_label = QLabel("Loading...", self)
        self.price_label.setFont(QFont("Helvetica", 16))
        self.price_label.move(13, 25)

        self.update_interval = 30
        self.time_left = self.update_interval

        self.update_button = QPushButton(f"{self.update_interval} secs", self)
        self.update_button.clicked.connect(self.change_interval)
        self.update_button.resize(55,30)
        self.update_button.move(130, 30)

        self.timer_label = QLabel(f"next update: {self.time_left} secs", self)
        self.timer_label.setFont(QFont("Helvetica", 8))
        self.timer_label.resize(105,35)
        self.timer_label.move(10, 50)

        close_button = QPushButton("X", self)
        close_button.clicked.connect(self.close)
        close_button.resize(30,20)
        #close_button.move(self.width() - 40, 0)
        close_button.move(160, 0)

        self.timer = QTimer()
        self.timer.timeout.connect(self.countdown_timer)
        self.timer.start(1000)

        # Update the price on startup
        self.update_price()

        self.show()

    def change_interval(self):
        if self.update_interval == 10:
            self.update_interval = 30
        elif self.update_interval == 30:
            self.update_interval = 60
        elif self.update_interval == 60:
            self.update_interval = 300
        else:
            self.update_interval = 10
        self.update_button.setText(f"{self.update_interval} secs")

    def update_price(self):
        response = requests.get("https://api.dexie.space/v1/offers?requested=USDS&offered=XCH&compact=true&page_size=1")
        data = response.json()
        price = data['offers'][0]['price']
        self.price_label.setText(f"Price: ${price}")

    def countdown_timer(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.timer_label.setText(f"next update: {self.time_left} secs")
        else:
            self.update_price()
            self.time_left = self.update_interval

app = QApplication(sys.argv)
monitor = PriceMonitor()
sys.exit(app.exec_())
