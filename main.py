import sys
import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget, QLabel, QVBoxLayout, QSizePolicy
from PyQt6.QtCore import QTimer, Qt, QRect
from datetime import datetime

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
        
        self.game_timer = QTimer(self)
        self.game_timer.setSingleShot(True) #sets how long each game lasts

        self.setWindowTitle("Whack a mole")
        self.setGeometry(500, 500, 500, 500)
        self.preset_home_menu()
        self.preset_game_graphics()

        self.setCentralWidget(self.menu_widget)
        
    def preset_home_menu(self):
        self.menu_widget = QWidget()
        self.menu_widget.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self.menu_widget.setStyleSheet("background: #D98324;")

        self.mnlyout = QVBoxLayout(self.menu_widget)
        self.mnlyout.setContentsMargins(40, 100, 40, 150)

        self.menu_ttl = QLabel("Whack-A-Mole")
        self.menu_ttl.setStyleSheet(
            "color: black;"
            "font-size: 40px;"
            "font-family: 'Consolas';"
        )
        self.menu_ttl.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.start_game_button = QPushButton("Start Game")
        self.start_game_button.clicked.connect(self.load_game_instance)
        self.start_game_button.setFixedSize(200, 60)
        self.start_game_button.setStyleSheet("""
            *{
            border: 1px solid 'black';
            border-radius: 10px;
            font-family: 'Consolas';
            background: 'lightgreen';
            color: 'black';
            }
            *:hover{
            border: 1px solid 'black';
            border-radius: 10px;
            font-family: 'Consolas';
            background: 'green';
            color: 'white';
            }
            """   
        )

        self.settings_button = QPushButton("Settings")
        self.settings_button.setFixedSize(200, 60)
        self.settings_button.setStyleSheet("""
            *{
            border: 1px solid 'black';
            border-radius: 10px;
            font-family: 'Consolas';
            background: '#ffc640';
            color: 'black';
            }
            *:hover{
            border: 1px solid 'black';
            border-radius: 10px;
            font-family: 'Consolas';
            background: '#6e5314';
            color: 'white';
            }
            """ 
        )

        self.mnlyout.addWidget(
            self.menu_ttl, 
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        self.mnlyout.addSpacing(70)
        self.mnlyout.addWidget(
            self.start_game_button, 
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        self.mnlyout.addSpacing(30)
        self.mnlyout.addWidget(
            self.settings_button, 
            alignment=Qt.AlignmentFlag.AlignCenter
        )

    def preset_game_graphics(self):
        self.game_widget = QWidget() #creates the gameplay widget
        self.game_widget.setStyleSheet("background: #D98324;")
        self.glyout = QVBoxLayout(self.game_widget)

        self.score_ui = QLabel(f"Score: 0") #counter stylesheets
        self.score_ui.setFixedSize(160, 60)
        self.score_ui.setStyleSheet(
            "border: 2px solid grey;"
            "border-radius: 10px;"
            "background: white;"
            "color: black;"
            "font-size: 20px;"
            "font-family: 'Times New Roman'"
        )
        self.score_ui.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.grid_layout = QGridLayout()
        self.buttons = [] #buttons array
        for row in range(GRID_SIZE): #creates 4 columns
            for col in range(GRID_SIZE): #creates a column of 4 buttons
                self.button = QPushButton("")
                self.button.setFixedSize(DFLT_BTN_W, DFLT_BTN_H)
                self.button.setStyleSheet(
                    "background: #291528;"
                    "border-radius: 42;"
                    "border: 7px solid #DFE0F2;"
                    "color: white;"
                    "font-size: 20px;"
                )
                self.grid_layout.addWidget(self.button, row, col)
                self.buttons.append(self.button) #puts the created button instances into an array
                self.button.clicked.connect(self.whack) #detects button click and calls whack function       

        self.glyout.addWidget(self.score_ui, alignment=Qt.AlignmentFlag.AlignCenter, stretch=1)
        self.glyout.addLayout(self.grid_layout, stretch=4)

    def countdown(self): #add game start countdown ui later
        pass

    def load_game_instance(self):
        self.total_movements = 0 #counts the total potential points in any single game
        self.forced_movements = 0 #points
        self.setCentralWidget(self.game_widget) #puts the gameplay screen on the main window
        self.now = datetime.now().strftime("%d/%m/%Y, %I:%M %p")
        QTimer.singleShot(2000, self.run_game_instance) #runs game instance after 2 seconds

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
            self.mole_move(
                self.whacked_button, 
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
        QTimer.singleShot(
            75, 
            lambda: self.whacked_button.setStyleSheet(
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
        try:
            self.assess_score()
            self.append_score()
        except ZeroDivisionError: #if for SOME REASON the total_movements didn't register or mole didn't move, the game won't crash
            print("Error: It appears that the mole did not move, or mole doesn't exist")
        QApplication.quit()

    def assess_score(self):
        self.accuracy = (self.forced_movements / self.total_movements) * 100
        self.misses = self.total_movements - self.forced_movements
        if self.accuracy >= 95: #evaluates final rank based on accuracy
            self.rank = "S"
        elif self.accuracy >= 80:
            self.rank = "A"
        elif self.accuracy >= 60:
            self.rank = "B"
        elif self.accuracy >= 40:
            self.rank = "C"
        elif self.accuracy >= 10:
            self.rank = "D"
        elif self.accuracy >= 0:
            self.rank = "F"
        else:    
            self.rank = "undefined"

    def append_score(self):
        with open("score.txt", "a", encoding="utf-8") as file: #only records score when player actually finishes a game without exiting (might change in the future)
            file.write(f"Game Instance created: {self.now};\n")
            file.write(f"Finished in {game_duration} seconds;\n")
            file.write(f"Score: {self.forced_movements};\n")
            file.write(f"Misses: {self.misses};\n")
            file.write(f"Accuracy: {round(self.accuracy, 1)}%;\n")
            file.write(f"Rank: {self.rank}\n\n")
        print("Appended score to text file at TBA Path") #debugging for those who can't find their score.txt (future)

           
app = QApplication(sys.argv)
window = MyFirstWindow() #finalizes the window
window.show()
sys.exit(app.exec())
