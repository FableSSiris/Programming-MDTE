import sys
import random
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QStackedWidget, QComboBox, QSlider
from PyQt6.QtCore import QTimer, Qt
from PyQt6.QtGui import QCursor
from datetime import datetime

mole_count = 2
grid_size = 4 #default 4x4; only 3 - 5 for now please don't bother with any larger or smaller
DFLT_BTN_W = 186
DFLT_BTN_H = 180
mole_speed_min = 900
mole_speed_max = 1500
DEFAULT_GAME_DURATION = 15 #in seconds

class EndScreenWidget(QWidget): #1. This class is required otherwise the endscreen widget won't overlay
    def __init__(
        self, 
        home_callback, #argument that accepts a function
        play_again_callback, #---
        parent=None #argument to set a parent when class is called
    ):
        super().__init__(parent)

        self.setObjectName("overlay")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setContentsMargins(40, 30, 40, 30)
        self.setStyleSheet("""
            #overlay {
                border: 4px solid black;
                background: #289911;
                border-radius: 15px;
                border: 4px solid #ffff21;    
            }
        """)

        self.hide()
        lyout = QVBoxLayout(self) #vertical layout
        lyout.setSpacing(0)
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        # 2. Enable mouse clicks from going through to widgets below 
        #self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        
        # Add some content to the overlay
        self.label = QLabel("Rank:", alignment=Qt.AlignmentFlag.AlignCenter)
        self.label.setMinimumHeight(120)
        self.label.setStyleSheet(
            "color: black;" \
            "background: white;" \
            "font-size: 40px;" \
            "font-family: 'Consolas';" \
            "font-weight: bold;"
            "border-radius: 5px;"
            )

        self.s_label = QLabel("Score:", alignment=Qt.AlignmentFlag.AlignCenter)
        self.s_label.setMinimumSize(400, 120)
        self.s_label.setStyleSheet(
            "color: black;" \
            "background: white;" \
            "font-size: 30px;" \
            "font-family: 'Consolas';" \
            "font-style: italic;"            
            "border-radius: 5px;"
            )        

        self.home_button = QPushButton("Return Home")
        self.home_button.clicked.connect(home_callback)
        self.home_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.home_button.setStyleSheet("""
            *{
                background: #86e637;
                color: black;
                font-family: 'Verdana';
                font-size: 30px
            }   
            *:hover{
                background: #6eb038;
                color: black;
                font-family: 'Verdana';
                font-size: 30px
            }
        """)
        self.home_button.setMinimumHeight(120)

        self.again_button = QPushButton("Play Again")
        self.again_button.clicked.connect(play_again_callback)
        self.again_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.again_button.setStyleSheet("""
            *{
                background: #86e637;
                color: black;
                font-family: 'Verdana';
                font-size: 30px
            }   
            *:hover{
                background: #6eb038;
                color: black;
                font-family: 'Verdana';
                font-size: 30px
            }
        """)
        self.again_button.setMinimumHeight(120)

        btn_layout.addWidget(self.home_button)
        btn_layout.addWidget(self.again_button)

        lyout.addWidget(
            self.label, 
            alignment=Qt.AlignmentFlag.AlignTop
        )
        lyout.addWidget(
            self.s_label, 
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter
        )
        lyout.addSpacing(50)
        lyout.addLayout(btn_layout)
                

class MyFirstWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.game_duration = DEFAULT_GAME_DURATION
        self.game_id = 0 #this variable is a checker for anything that calls the mole_move functions;
        #once a new game starts, this variable prevents any zombie instances from creating complications, especially ones that require a recursive QTimer
        self.display_time = self.game_duration
        self.countdown_timer = QTimer(self) #display timer
        self.countdown_timer.timeout.connect(self.countdown)

        self.setWindowTitle("Whack a mole")
        self.resize(1000, 1000)
        self.preset_home_menu()
        self.preset_game_graphics()
        self.preset_settings()

        self.pages = QStackedWidget() #alternator for game/menu widget

        self.pages.addWidget(self.menu_widget)
        self.pages.addWidget(self.game_widget)
        self.pages.addWidget(self.settings_widget)

        self.setCentralWidget(self.pages)
        self.pages.setCurrentWidget(self.menu_widget)
        
    def preset_home_menu(self): #loads home menu onto a spread 
        self.menu_widget = QWidget()
        self.menu_widget.setMinimumSize(1000, 1000)
        self.menu_widget.setStyleSheet("background: #D98324;")

        mnlyout = QVBoxLayout(self.menu_widget)
        mnlyout.setContentsMargins(40, 150, 40, 250)

        menu_ttl = QLabel("Whack-A-Mole", alignment=Qt.AlignmentFlag.AlignCenter)
        menu_ttl.setStyleSheet(
            "color: black;"
            "font-size: 80px;"
            "font-family: 'Consolas';"
        )

        start_game_button = QPushButton("Start Game")
        start_game_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        start_game_button.clicked.connect(self.load_game_instance)
        start_game_button.setMinimumSize(400, 120)
        start_game_button.setStyleSheet("""
            *{
            font-size: 30px;
            border: 2px solid 'black';
            border-radius: 10px;
            font-family: 'Consolas';
            background: 'lightgreen';
            color: 'black';
            }
            *:hover{
            font-size: 30px;
            border: 2px solid 'black';
            border-radius: 10px;
            font-family: 'Consolas';
            background: 'green';
            color: 'white';
            }
        """)

        settings_button = QPushButton("Settings")
        settings_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        settings_button.clicked.connect(self.load_settings)
        settings_button.setMinimumSize(400, 120)
        settings_button.setStyleSheet("""
            *{
            font-size: 30px;
            border: 2px solid 'black';
            border-radius: 10px;
            font-family: 'Consolas';
            background: '#ffc640';
            color: 'black';
            }
            *:hover{
            font-size: 30px;
            border: 2px solid 'black';
            border-radius: 10px;
            font-family: 'Consolas';
            background: '#6e5314';
            color: 'white';
            }
        """)

        clear_score_button = QPushButton("clear score", parent=self.menu_widget) #developer function
        clear_score_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor)) #developer function
        clear_score_button.setStyleSheet("color: grey; background: white; border: 1px solid black") #developer function
        clear_score_button.move(20, 10) #developer function
        clear_score_button.clicked.connect(self.clear_score) #developer function caller (will be removed later)

        mnlyout.addWidget(
            menu_ttl, 
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        mnlyout.addSpacing(70)
        mnlyout.addWidget(
            start_game_button, 
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        mnlyout.addSpacing(10)
        mnlyout.addWidget(
            settings_button, 
            alignment=Qt.AlignmentFlag.AlignCenter
        )

    def preset_game_graphics(self):
        self.game_widget = QWidget() #creates the gameplay widget
        self.game_widget.setStyleSheet("background: #D98324;")

        self.uilyout = QHBoxLayout()
        self.uilyout.setContentsMargins(60, 15, 60, 15)
        self.score_ui = QLabel(f"Score: 0", alignment=Qt.AlignmentFlag.AlignCenter) #counter stylesheets
        self.score_ui.setMinimumSize(320, 120)
        self.score_ui.setStyleSheet(
            "border: 2px solid grey;"
            "border-radius: 10px;"
            "background: white;"
            "color: black;"
            "font-size: 40px;"
            "font-family: 'Times New Roman'"
        )
        self.timer_ui = QLabel(f"Time: {self.display_time}s", alignment=Qt.AlignmentFlag.AlignCenter)
        self.timer_ui.setMinimumSize(320, 120)
        self.timer_ui.setStyleSheet(
            "border: 2px solid grey;"
            "border-radius: 10px;"
            "background: white;"
            "color: black;"
            "font-size: 40px;"
            "font-family: 'Times New Roman'"
        )
        self.uilyout.addWidget(
            self.timer_ui, 
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        self.uilyout.addWidget(
            self.score_ui, 
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        self.grid_layout = QGridLayout() #game grid layout
        self.grid_layout.setSpacing(10)
        self.buttons = [] #buttons array
        for row in range(grid_size): #creates 4 columns
            for col in range(grid_size): #creates a column of 4 buttons
                button = QPushButton("")
                button.setMinimumSize(DFLT_BTN_W, DFLT_BTN_H)
                button.setStyleSheet(
                    "background: #291528;"
                    "border-radius: 84px;"
                    "border: 7px solid #DFE0F2;"
                    "color: white;"
                    "font-size: 40px;"
                )
                button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                self.grid_layout.addWidget(button, row, col)
                self.buttons.append(button) #puts the created button instances into an array
                button.clicked.connect(self.whack) #detects button click and calls whack function 
     
        self.glyout = QVBoxLayout(self.game_widget)
        self.glyout.setContentsMargins(20, 0, 20, 5)
        self.glyout.addLayout(self.uilyout)
        self.glyout.addLayout(self.grid_layout)
        self.overlay = EndScreenWidget( #calls EndScreenWidget class as an object in MyFirstWindow
            self.load_home, 
            self.load_game_instance, 
            self.game_widget
        )

        self.mole_queue = [] #list that contains the id of each mole, might be useful in the future

    def preset_settings(self):
        self.settings_widget = QWidget()
        self.settings_widget.setStyleSheet("background: green")

        st_layout = QVBoxLayout(self.settings_widget)
        slider_layout = QHBoxLayout()
        grid_setting_layout = QHBoxLayout()

        return_button = QPushButton("Return")
        return_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        return_button.setStyleSheet("""
            border: 1px solid black; \
            color: black;
            background: white;
            font-size: 40px
        """)
        return_button.clicked.connect(self.load_home)

        display_grid_setting = QLabel("Grid Layout (WIP)")

        set_grid_size = QComboBox()
        set_grid_size.setStyleSheet("background: white; color: black; font-size: 40px")
        set_grid_size.addItems(["3x3", "4x4", "5x5"])
        set_grid_size.setCurrentIndex(grid_size - 3) #3x3 grid size is index 0, 4x4 is 1, etc. ^^^^

        self.display_game_duration = QLabel(
            f"Game Duration: {self.game_duration}s"
        )
        self.display_game_duration.setMinimumSize(300, 50)
        self.display_game_duration.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display_game_duration.setStyleSheet("""
            font-size: 30px;
            color: black;
            border: 2px solid 'dark-green';
            background: white;
            font-family: 'Times New Roman'
        """)

        set_game_time = QSlider(Qt.Orientation.Horizontal)
        set_game_time.setValue(self.game_duration)
        set_game_time.valueChanged.connect(self.change_game_duration)
        set_game_time.sliderReleased.connect(
            lambda: print(f"Game duration changed to {self.game_duration} seconds")
        )
        set_game_time.setStyleSheet("""
            QSlider::groove:horizontal {
                height: 16px;
                background: grey;
                border-radius: 4px;
                border: 2px solid orange;
            }
            QSlider::handle:horizontal {
                background: red;
                width: 36px;
                border: 2px solid orange;
                height: 36px;
                margin: -10px 0;
                border-radius: 9px;
            }
        """)
        set_game_time.setMinimumSize(800, 50)
        set_game_time.setRange(5, 60)

        grid_setting_layout.addWidget(display_grid_setting)
        grid_setting_layout.addWidget(set_grid_size)

        slider_layout.addWidget(set_game_time)
        slider_layout.addSpacing(20)
        slider_layout.addWidget(self.display_game_duration)
        slider_layout.setContentsMargins(40, 0, 40, 0)

        st_layout.addWidget(return_button)
        st_layout.addSpacing(400)
        st_layout.addLayout(grid_setting_layout)
        st_layout.addSpacing(200)
        st_layout.addLayout(slider_layout)
        st_layout.setContentsMargins(50, 50, 50, 150)

    def change_game_duration(self, value):
        self.game_duration = value
        self.display_game_duration.setText(
            f"Game duration: {value}s"
        )

    def load_home(self):
        self.overlay.hide()
        self.pages.setCurrentWidget(self.menu_widget)

    def load_settings(self):
        self.overlay.hide()
        self.pages.setCurrentWidget(self.settings_widget)

    def load_game_instance(self):
        self.game_id += 1

        self.clear_all_moles()

        self.total_mole_movements = 0 #counts the total potential points in any single game
        self.successful_hits = 0 #points
        self.score_ui.setText(f"Score: {self.successful_hits}")
        self.display_time = self.game_duration
        self.timer_ui.setText(f"Get Ready")

        self.pages.setCurrentWidget(self.game_widget) #puts the gameplay screen on the main window
        self.overlay.hide()
        
        QTimer.singleShot(0, self.resize_overlay)

        self.now = datetime.now().strftime("%d/%m/%Y, %I:%M %p")
        QTimer.singleShot(2000, self.run_game_instance) #runs game instance after 2 seconds

    def resize_overlay(self): #helper function because the overlay QLabel's size is janky when first loaded
        parent_rect = self.game_widget.rect()
        overlay_width = int(parent_rect.width() * 0.8)
        overlay_height = int(parent_rect.height() * 0.65)

        x = (parent_rect.width() - overlay_width) // 2
        y = (parent_rect.height() - overlay_height) // 2

        self.overlay.setGeometry(
            x,
            y,
            overlay_width,
            overlay_height
        )
        self.overlay.raise_()

    def run_game_instance(self): #starts game, initiates moles, spawns a mole per mole count every 
        self.timer_ui.setText(f"Time: {self.game_duration}s")
        
        self.mole_queue = [] 
        if len(self.mole_queue) == 0: #check for an empty list before actually appending moles else they duplicate
            for i in range(mole_count):
                self.mole_queue.append(f"MOLE{i}")

        QTimer.singleShot(self.game_duration * 1000, self.end_game_instance)


        self.countdown_timer.start(1000)

        self.mole_index = 0

        self.spawn_timer = QTimer(self)
        self.spawn_timer.setSingleShot(True)
        self.spawn_timer.timeout.connect(self.next_mole)

        self.start_next()

    def countdown(self): #add game start countdown ui later
        #get the current time and set it on the label
        if self.display_time > 0:
            self.display_time -= 1
            self.timer_ui.setText(f"Time: {self.display_time}s")
        else:
            self.countdown_timer.stop()
            
    def whack(self):
        """
        when the mole is whacked, also resets move_time
        so mole movement can be controlled to some degree by the player
        """
        button = self.sender() 
        if button.text() != "":
            mole = button.text()
            self.mole_move(button, mole, self.game_id)
            self.whack_effect(button, True)
            button.setText("")
            self.successful_hits += 1
            self.score_ui.setText(f"Score: {self.successful_hits}")
        else:
            self.total_mole_movements += 1
            self.whack_effect(button)

    def whack_effect(self, button, isHit=False): #border whack effect
        temp_file = button.styleSheet() #temporary file that stores stylesheet string

        if isHit:
            button.setStyleSheet(
                temp_file + "border: 10px solid #39fc03;"
            )
        else:
            button.setStyleSheet(
                temp_file + "border: 9px solid #DFE0F2;"
            )

        temp_file = button.styleSheet()
        QTimer.singleShot(
            75, 
            lambda: button.setStyleSheet(
                temp_file + "border: 7px solid #DFE0F2;"
            )
        )

    def start_next(self): #prepares next mole appearing during start up, checks if max mole count has been reached
        if self.mole_index < len(self.mole_queue):
            delay = random.randint(1, 4) * 250
            self.spawn_timer.start(delay)

    def next_mole(self): #calls for next mole if max mole hasn't been reached
        mole_num = self.mole_queue[self.mole_index]

        self.create_moles(mole_num)

        self.mole_index += 1
        self.start_next()
        
    def create_moles(self, mole_num): #displays mole text on the board, terminates 

        empty_buttons = [btn for btn in self.buttons if btn.text() == ""] #vacancy condition for spawning a mole

        if empty_buttons: #checks for a vacant button to place the mole
            vacancy = random.choice(empty_buttons) #picks a random valid location to spawn the mole
            vacancy.setText(mole_num)

            print(f"Created {mole_num}") #this is for debugging

        move_time = random.randint(mole_speed_min, mole_speed_max)
        current_game = self.game_id
        QTimer.singleShot(
            move_time, 
            lambda: self.mole_move(
                vacancy, 
                mole_num, 
                current_game
            )
        ) #code for forcing mole to move after a set time
        
    def mole_move(self, btn, which_mole, game_id):
        if game_id != self.game_id:
            return

        if btn.text() != which_mole:
            return
        
        empty_buttons = [
            bt for bt in self.buttons 
            if bt.text() == ""
            ] #checks for empty buttons

        move_time = random.randint(mole_speed_min, mole_speed_max)
        
        if empty_buttons: 
            btn.setText("") 
            vacancy = random.choice(empty_buttons) #checks for a vacant button to move the mole
            vacancy.setText(which_mole)
            self.total_mole_movements += 1 #adds a count to total potential points

            current_game = self.game_id

            QTimer.singleShot(
                move_time,
                lambda: self.mole_move(vacancy, which_mole, current_game)
            )
        else: #treats boundaries and invalid inputs as program quits **for now**
            QApplication.quit() #the game crashes if the board becomes filled with same or more moles for each hole due to famine
            print("!!!!!the game crashed due to overpopulation!!!!!")

    def end_game_instance(self):
        self.clear_all_moles()
        try:
            self.assess_score()
        except ZeroDivisionError: #if for SOME REASON the total_mole_movements didn't register or mole didn't move, the game won't crash
            print("ZeroDivisionError: It appears that the mole did not move, or mole doesn't exist")
        self.evaluate_rank()
        self.append_score()
        self.toggle_endscreen()

    def toggle_endscreen(self):
        self.overlay.label.setText(f"Rank: {self.rank}")
        self.overlay.s_label.setText(f"Score: {self.successful_hits}")

        if self.overlay.isVisible():
            self.overlay.hide()
        else:
            self.overlay.again_button.setDisabled(True) # Prevents accidentally restarting/exiting
            self.overlay.home_button.setDisabled(True)  # Prevents accidentally restarting/exiting
            self.overlay.show()
            QTimer.singleShot(750, lambda: self.overlay.again_button.setDisabled(False)) # Prevents accidentally restarting/exiting
            QTimer.singleShot(750, lambda: self.overlay.home_button.setDisabled(False)) # Prevents accidentally restarting/exiting

    def clear_all_moles(self): #function name
        for button in self.buttons:
            button.setText("")

    def assess_score(self): #function name
        if self.total_mole_movements == 0: #prevents ZeroDivisionError from ever occurring
            self.accuracy = -1
            self.misses = 0
            return

        self.accuracy = (self.successful_hits / self.total_mole_movements) * 100

        self.misses = self.total_mole_movements - self.successful_hits

    def evaluate_rank(self):
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

    def append_score(self): #records the score in a text document
        if self.accuracy == -1:
            print("Result was not appended.")
            return
        # debugging #
        print(f"Game Instance created: {self.now};")
        print(f"Finished in {self.game_duration} seconds;")
        print(f"Score: {self.successful_hits};")
        print(f"Misses: {self.misses};")
        print(f"Accuracy: {round(self.accuracy, 1)}%;")
        print(f"Rank: {self.rank}")
        # debugging #    

        with open("score.txt", "a", encoding="utf-8") as file: #only records score when player actually finishes a game without exiting (might change in the future)
            file.write(f"Game Instance created: {self.now};\n")
            file.write(f"Finished in {self.game_duration} seconds;\n")
            file.write(f"Score: {self.successful_hits};\n")
            file.write(f"Misses: {self.misses};\n")
            file.write(f"Accuracy: {round(self.accuracy, 1)}%;\n")
            file.write(f"Rank: {self.rank}\n\n")
        print("Appended score to text file at TBA Path") #debugging for those who can't find their score.txt (future)

    def clear_score(self): #developer function
        with open("score.txt", "w", encoding="utf-8") as file:
            pass
        print("cleared score.txt")

    def resizeEvent(self, event):
        super().resizeEvent(event)
        # Match the overlay's size to the target widget's exact current size
        if hasattr(self, "overlay"):
            self.resize_overlay()

           
app = QApplication(sys.argv)
window = MyFirstWindow() #finalizes the window
window.show()
sys.exit(app.exec())
