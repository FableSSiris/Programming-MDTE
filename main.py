import sys
import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget
from PyQt6.QtCore import QTimer

LIGHT_GREEN = "#55a12d"
GREEN = "#0f0"
BROWN = "brown"
mole_speed = random.randint(1, 4)
MOLE_COUNT = 3
timer = QTimer()


class MyFirstWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Whack a mole")
        self.resize(500, 500)

        self.grid_layout = QGridLayout()
        self.buttons = [] #buttons array
        for row in range(4): #creates 4 columns
            for col in range(4): #creates a column of 4 buttons
                self.button = QPushButton("")
                self.button.setFixedSize(93, 85)
                self.button.setIcon
                self.button.setStyleSheet(
                    f"background-color: #291528;"
                    "border-radius: 42;"
                    f"border: 7px solid #DFE0F2;"
                    f"color: white"
                    )
                self.grid_layout.addWidget(self.button, row, col)
                self.buttons.append(self.button) #puts the created button instances into an array
                self.button.clicked.connect(self.button_clicked) #detects button click and calls button_clicked function           

        self.game_widget = QWidget() #creates the gameplay widget
        self.game_widget.setLayout(self.grid_layout)
        self.game_widget.setStyleSheet(f"background-color: #D98324")

        self.setCentralWidget(self.game_widget) #puts the gameplay screen on the main window
        timer.singleShot(2000, self.game_instance) #loads game instance
        
    def button_clicked(self):
        self.selected_button = self.sender()
        if self.selected_button.text() == "MOLE":
            self.selected_button.setText("")
            self.mole_count.remove("MOLE")
            #print(self.mole_count) #this is for debugging

    def game_instance(self): 
        self.mole_count = []
        timer.timeout.connect(lambda: self.create_moles(MOLE_COUNT))
        timer.start(mole_speed * 250) #250 ms = 0.25s constant; mole_speed is a positive real integer

    def mole_movement(self): #future function that will control whether moles disappear or instantly pop out from a different hole
        pass

    def create_moles(self, total_count):
        global mole_speed
        random_button = random.choice(self.buttons)  
        if self.mole_count.count("MOLE") >= total_count:
            pass
        elif random_button.text() == "": #checks for vacant mole placement
            self.selected_button = random_button
            self.selected_button.setText("MOLE")
            self.mole_count.append("MOLE")
            mole_speed = random.randint(1, 4) #randomizes the period of each new mole
            timer.start(mole_speed * 250) #resets the period on timer
            #print(self.mole_count) #debugging
        else: #recalls the function and tries again if mole placement is preoccupied
            self.create_moles(total_count)
        

app = QApplication(sys.argv)
window = MyFirstWindow() #finalizes the window
window.show()
sys.exit(app.exec())
print('Hello World!')
