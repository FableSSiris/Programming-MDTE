import sys
import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget, QLabel, QVBoxLayout, QHBoxLayout
from PyQt6.QtCore import QTimer, Qt

LIGHT_GREEN = "#55a12d"
GREEN = "#0f0"
BROWN = "brown"
mole_count = 1
GRID_SIZE = 4
DFLT_BTN_W = 93
DFLT_BTN_H = 85
game_duration = 30


class MyFirstWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.total_movements = 0 #counts the total potential points in any single game
        self.forced_movements = 0 #points
        
        self.game_timer = QTimer(self)
        self.game_timer.setSingleShot(True) #sets how long each game lasts

        self.setWindowTitle("Whack a mole")
        self.resize(500, 500)
        self.load_game_graphics()

        self.setCentralWidget(self.game_widget) #puts the gameplay screen on the main window
        QTimer.singleShot(2000, self.run_game_instance) #runs game instance after 2 seconds
        

    def load_game_graphics(self):
        self.game_widget = QWidget() #creates the gameplay widget
        self.lyout = QVBoxLayout(self.game_widget)

        self.score_ui = QLabel(f"Score: 0") #counter stylesheets
        self.score_ui.setFixedSize(160, 30)
        self.score_ui.setStyleSheet(
            "border: 1px solid black;"
            "background-color: white;"
            "color: black;"
            "font-size: 20px;"
            "font-family: 'Times New Roman'")
        self.score_ui.setAlignment(Qt.AlignmentFlag.AlignCenter)

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

        self.lyout.addWidget(self.score_ui, alignment=Qt.AlignmentFlag.AlignCenter, stretch=1)
        self.lyout.addLayout(self.grid_layout, stretch=4)
        self.game_widget.setStyleSheet("background-color: #D98324;")

    def countdown(self): #add game start countdown later
        pass

    def run_game_instance(self): 
        self.mole_closet = [] #list that contains the id of each mole, might be useful in the future
        for i in range(mole_count):
            self.mole_closet.append(f"MOLE{i}")

        QTimer.singleShot(game_duration * 1000, self.end_game_instance)

        self.mole_index = 0

        self.spawn_timer = QTimer(self)
        self.spawn_timer.setSingleShot(True)
        self.spawn_timer.timeout.connect(self.next_mole)

        self.start_next()
    
    def whack(self):
        """
        when the mole is whacked, also resets move_time
        so mole movement can be controlled to some degree by the player
        """
        self.whacked_button = self.sender() 
        if self.whacked_button.text() != "":
            self.mole_move(self.whacked_button, 
                           self.whacked_button.text()
                           )
            self.whack_effect(True)
            self.whacked_button.setText("")
            self.forced_movements += 1
            self.score_ui.setText(f"Score: {self.forced_movements}")
        else:
            self.whack_effect()

    def whack_effect(self, isHit=False): #border whack effect
        temp_file = self.whacked_button.styleSheet()
        if isHit:
            self.whacked_button.setStyleSheet(
                temp_file + "border: 10px solid #39fc03;"
                )
        else:
            self.whacked_button.setStyleSheet(
                temp_file + "border: 9px solid #DFE0F2;"
                )

        temp_file = self.whacked_button.styleSheet()
        QTimer.singleShot(75, lambda: 
                self.whacked_button.setStyleSheet(
                    temp_file + "border: 7px solid #DFE0F2;"
                    )
                )

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
            self.total_movements += 1 #adds a count to total potential points

            QTimer.singleShot(
            move_time,
            lambda: self.mole_move(vacancy, which_mole)
            )
        else: #treats boundaries and invalid inputs as program quits **for now**
            QApplication.quit() #the game crashes if the board becomes filled with same or more moles for each hole due to famine
            print("!!!!!the game crashed due to overpopulation!!!!!")

    def end_game_instance(self):
        QApplication.quit()
        try:
            accuracy = (self.forced_movements / self.total_movements) * 100
            print(f"Points: {self.forced_movements}")
            print(f"Accuracy: {round(accuracy, 1)}%")
        except ZeroDivisionError:
            print(f"Points: {self.forced_movements}")
            print("Stupid Monkey who can't even see moles")
        
            
app = QApplication(sys.argv)
window = MyFirstWindow() #finalizes the window
window.show()
sys.exit(app.exec())
