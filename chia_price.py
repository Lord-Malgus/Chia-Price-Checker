from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QSlider
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QFont
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
    def open_url(self):
        import webbrowser
        webbrowser.open("https://dexie.space/offers/XCH/USDS")
    
    def change_opacity(self):
        opacity = float(self.opacity_slider.value()) / 100
        self.setWindowOpacity(opacity)

    def __init__(self):
        super().__init__()        
        self.resize(207, 80)
        self.move(QApplication.desktop().screen().rect().center()- self.rect().center())
        self.title_label = QLabel("<a style='color: green' href='https://dexie.space/offers/XCH/USDS'>Dexie Chia Price</a>", self)
        self.title_label.setFont(QFont("Helvetica", 9))
        self.title_label.move (10,-5)
        self.title_label.setTextInteractionFlags(Qt.LinksAccessibleByMouse | Qt.LinksAccessibleByKeyboard)
        self.title_label.linkActivated.connect(self.open_url)
        self.price_label = QLabel("Loading...", self)
        self.price_label.setFont(QFont("Helvetica", 16))
        self.price_label.resize(128,25)
        self.price_label.move(6, 25)

        self.opacity_slider = QSlider(Qt.Horizontal, self)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setSingleStep(1)
        self.opacity_slider.setValue(100)
        self.opacity_slider.setWindowOpacity(1.0)
        self.opacity_slider.valueChanged.connect(self.change_opacity)
        self.opacity_slider.resize(50,10)
        self.opacity_slider.move(155, 65)

        self.update_interval = 30
        self.time_left = self.update_interval

        self.update_button = QPushButton(f"{self.update_interval} secs", self)
        self.update_button.clicked.connect(self.change_interval)
        self.update_button.resize(55,30)
        self.update_button.move(150, 30)

        self.timer_label = QLabel(f"next update: {self.time_left} secs", self)
        self.timer_label.setFont(QFont("Helvetica", 8))
        self.timer_label.resize(105,35)
        self.timer_label.move(10, 50)

        close_button = QPushButton("X", self)
        close_button.clicked.connect(self.close)
        close_button.resize(25,20)
        close_button.move(180, 0)

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
        self.price_label.setText(f"${price}")

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
