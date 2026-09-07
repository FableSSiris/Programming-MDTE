import sys
import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget
from PyQt6.QtCore import QTimer

LIGHT_GREEN = "#55a12d"
GREEN = "#0f0"
BROWN = "brown"
mole_count = 3
GRID_SIZE = 4
DFLT_BTN_W = 93
DFLT_BTN_H = 85


class MyFirstWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Whack a mole")
        self.resize(500, 500)

        self.load_game_graphics()
        QTimer.singleShot(2000, self.run_game_instance) #runs game instance after 2 seconds

    def load_game_graphics(self):
        self.grid_layout = QGridLayout()

        self.buttons = [] #buttons array
        for row in range(GRID_SIZE): #creates 4 columns
            for col in range(GRID_SIZE): #creates a column of 4 buttons
                self.button = QPushButton("")
                self.button.setFixedSize(DFLT_BTN_W, DFLT_BTN_H)
                self.button.setStyleSheet(
                    "background-color: #291528;"
                    "border-radius: 42;"
                    "border: 7px solid #DFE0F2;"
                    "color: white;"
                    "font-size: 20px;"
                    )
                self.grid_layout.addWidget(self.button, row, col)
                self.buttons.append(self.button) #puts the created button instances into an array
                self.button.clicked.connect(self.whack) #detects button click and calls whack function       

        self.game_widget = QWidget() #creates the gameplay widget
        self.game_widget.setLayout(self.grid_layout)
        self.game_widget.setStyleSheet("background-color: #D98324;")

        self.setCentralWidget(self.game_widget) #puts the gameplay screen on the main window

    def countdown(self): #add game start countdown later
        pass

    def run_game_instance(self): 
        self.mole_closet = []
        for i in range(mole_count):
            self.mole_closet.append(f"MOLE{i}")

        self.mole_index = 0

        self.spawn_timer = QTimer(self)
        self.spawn_timer.setSingleShot(True)
        self.spawn_timer.timeout.connect(self.next_mole)

        self.start_next()
    
    def whack(self): #when button clicks the mole
        self.whacked_button = self.sender() 
        if self.whacked_button.text() != "":
            self.mole_move(self.whacked_button, 
                           self.whacked_button.text()
                           )
            self.whacked_button.setText("")

    def start_next(self): #prepares next mole appearing during start up, checks if max mole count has been reached
        if self.mole_index < len(self.mole_closet):
            delay = random.randint(1, 4) * 250
            self.spawn_timer.start(delay)

    def next_mole(self): #calls for next mole if max mole hasn't been reached
        mole_num = self.mole_closet[self.mole_index]

        self.create_moles(mole_num)

        self.mole_index += 1
        self.start_next()
        
    def create_moles(self, mole_num): #displays mole text on the board
        empty_buttons = [btn for btn in self.buttons if btn.text() == ""] #vacancy condition for spawning a mole

        if empty_buttons: #checks for a vacant button to place the mole
            vacancy = random.choice(empty_buttons) #picks a random valid location to spawn the mole
            vacancy.setText(mole_num)

            print(mole_num) #this is for debugging

        move_time = random.randint(900, 1500)
        QTimer.singleShot(move_time, lambda: self.mole_move(vacancy, mole_num)) #code for forcing mole to move after a set time
        
    def mole_move(self, btn, which_mole):
        if btn.text() != which_mole:
            return
        
        empty_buttons = [
            bt for bt in self.buttons 
            if bt.text() == ""
            ] #checks for empty buttons

        move_time = random.randint(900, 1500)
        
        if empty_buttons: 
            btn.setText("") 
            vacancy = random.choice(empty_buttons) #checks for a vacant button to move the mole
            vacancy.setText(which_mole)

            QTimer.singleShot(
            move_time,
            lambda: self.mole_move(vacancy, which_mole)
            )
        else: #treats boundaries and invalid inputs as program quits for now
            QApplication.quit() #the game crashes if the board becomes filled with same or more moles for each hole due to famine
            

app = QApplication(sys.argv)
window = MyFirstWindow() #finalizes the window
window.show()
sys.exit(app.exec())
