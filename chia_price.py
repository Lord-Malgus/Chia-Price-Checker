from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QSlider, QCheckBox
from PyQt5.QtCore import Qt, QTimer, QPoint
from PyQt5.QtGui import QFont
import sys
import requests

# Create a custom main window class that can be moved around the screen
# by handling the mouse events to store the position of the window
# when the mouse is pressed and move the window when the mouse is dragged
class TitleBar(QMainWindow):
    def __init__(self, *args, **kwargs):
        # Initialize the QMainWindow
        super().__init__(*args, **kwargs)
        # Set the window flags to frameless to create a custom title bar
        self.setWindowFlags(Qt.FramelessWindowHint)

    # Override the mousePressEvent method to store the position of the window when the mouse is pressed
    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    # Override the mouseMoveEvent method to move the window when the mouse is dragged
    def mouseMoveEvent(self, event):
        delta = QPoint (event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()

# Create a custom main window class to display the Chia price
class PriceMonitor(TitleBar):
    # Method to open the Chia price website when the link is clicked
    def open_url(self):
        import webbrowser
        webbrowser.open("https://dexie.space/offers/XCH/USDS")
    
    # Method to change the opacity of the window when the slider is adjusted
    def change_opacity(self):
        opacity = float(self.opacity_slider.value()) / 100
        self.setWindowOpacity(opacity)

    # Method to handle the pinning of the window when the checkbox is clicked
    def pin_window(self, state):
        if state == Qt.Checked:
            self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(Qt.FramelessWindowHint)            
        self.show()

    def __init__(self):
        # Initialize the custom TitleBar main window
        super().__init__()        
        # Set the size and position of the window
        self.resize(207, 80)
        self.move(QApplication.desktop().screen().rect().center()- self.rect().center())
        # Create a label to display the link to the dexie website
        self.title_label = QLabel("<a style='color: green' href='https://dexie.space/offers/XCH/USDS'>Dexie Chia Price</a>", self)
        self.title_label.setFont(QFont("Arial", 9))
        self.title_label.move (10,-5)
        self.title_label.setTextInteractionFlags(Qt.LinksAccessibleByMouse | Qt.LinksAccessibleByKeyboard)
        self.title_label.linkActivated.connect(self.open_url)
        # Create a label to display the Chia price
        self.price_label = QLabel("Loading...", self)
        self.price_label.setFont(QFont("Arial", 16))
        self.price_label.resize(128,25)
        self.price_label.move(6, 25)

        # Create a slider to adjust the opacity
        self.opacity_slider = QSlider(Qt.Horizontal, self)
        self.opacity_slider.setRange(0, 100)
        self.opacity_slider.setSingleStep(1)
        self.opacity_slider.setValue(100)
        self.opacity_slider.setWindowOpacity(1.0)
        self.opacity_slider.valueChanged.connect(self.change_opacity)
        self.opacity_slider.resize(50,10)
        self.opacity_slider.move(155, 65)

        # Create a checkbox to pin the window
        self.checkbox = QCheckBox("pin",self)
        self.checkbox.setFont(QFont("Arial",7))
        self.checkbox.resize(32,18)
        self.checkbox.setChecked(False)
        self.checkbox.move(145,0)
        self.checkbox.stateChanged.connect(self.pin_window)
        
        self.update_interval = 30
        self.time_left = self.update_interval

        self.update_button = QPushButton(f"{self.update_interval} secs", self)
        self.update_button.clicked.connect(self.change_interval)
        self.update_button.resize(55,30)
        self.update_button.move(150, 30)

        self.timer_label = QLabel(f"next update: {self.time_left} secs", self)
        self.timer_label.setFont(QFont("Arial", 8))
        self.timer_label.resize(105,35)
        self.timer_label.move(10, 50)

        close_button = QPushButton("X", self)
        close_button.clicked.connect(self.close)
        close_button.resize(25,20)
        close_button.move(180, 0)

        # Create a timer to handle the countdown of the next price update
        self.timer = QTimer()
        self.timer.timeout.connect(self.countdown_timer)
        self.timer.start(1000)

        # Update the price on startup
        self.update_price()

        self.show()

# Method to change the interval between price updates
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

# Method to update the price by making an API call to the Chia price website
    def update_price(self):
        response = requests.get("https://api.dexie.space/v1/offers?requested=USDS&offered=XCH&compact=true&page_size=1")
        # Parse the JSON data from the API response
        data = response.json()
        # Get the price from the JSON data
        price = data['offers'][0]['price']
        # Update the price label with the new price
        self.price_label.setText(f"${price}")

# Method to handle the countdown timer for the next price update
    def countdown_timer(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.timer_label.setText(f"next update: {self.time_left} secs")
        else:
            self.update_price()
            self.time_left = self.update_interval

# Create the main application and the main window
app = QApplication(sys.argv)
window = QMainWindow()
# Create the PriceMonitor object
monitor = PriceMonitor()
# Start the main event loop and exit with the return code from `app.exec_()`
sys.exit(app.exec_())
