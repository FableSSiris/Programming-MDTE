import random
import sys
from datetime import datetime

from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QCursor
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QSizePolicy,
    QSlider,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

DEFAULT_MOLE_COUNT = 2  # max moles that can spawn per game, can be changed
grid_size = 4  # default 4x4; can be changed to 3x3 or 5x5 in settings
mole_speed_min = 900  # mole moves earliest after this many ms
mole_speed_max = 1500  # mole moves latest after this many ms
DEFAULT_GAME_DURATION = 5  # in seconds
MOLE_HOLE_STYLE = """
    background: #291528;
    border-radius: 84px;
    border: 7px solid #DFE0F2;
    color: white;
    font-size: 40px;
"""

class EndScreenWidget(QWidget): 
    """Display the end-game results over the gameplay screen."""  
    def __init__(
        self, 
        home_callback,  # argument that accepts a function
        play_again_callback, #---
        parent=None  # argument to set a parent when class is called
    ):
        super().__init__(parent)

        self.setObjectName("overlay")
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True)
        self.setContentsMargins(40, 30, 40, 30)
        self.setStyleSheet("""
            #overlay {
                background: #289911;
                border-radius: 15px;
                border: 4px solid #ffff21;    
            }
        """)

        self.hide()
        lyout = QVBoxLayout(self)
        lyout.setSpacing(0)
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)
        
        # Add some content to the overlay
        self.label = QLabel("Rank:", alignment=Qt.AlignmentFlag.AlignCenter)
        self.label.setMinimumHeight(120)
        self.label.setStyleSheet(
            self.label_style("black", "white", 40, 'Consolas', 'normal', 'bold', 5)
        )

        self.score_label = QLabel("Score:", alignment=Qt.AlignmentFlag.AlignCenter)
        self.score_label.setMinimumSize(400, 120)
        self.score_label.setStyleSheet(
            self.label_style("black", "white", 30, 'Consolas', 'italic', 'normal', 5)
        )

        self.home_button = QPushButton("Return Home")
        self.home_button.clicked.connect(home_callback)

        self.again_button = QPushButton("Play Again")
        self.again_button.clicked.connect(play_again_callback)

        for button in (self.home_button, self.again_button):
            button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            button.setMinimumHeight(120)
            button.setStyleSheet(
                self.button_style("#86e637", "#6eb038")
            )

        button_layout.addWidget(self.home_button)
        button_layout.addWidget(self.again_button)

        lyout.addWidget(
            self.label, 
            alignment=Qt.AlignmentFlag.AlignTop
        )
        lyout.addWidget(
            self.score_label, 
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter
        )
        lyout.addSpacing(50)
        lyout.addLayout(button_layout)

    def label_style(
        self,
        color,
        background,
        font_size,
        font_family,
        font_style,
        font_weight,
        border_radius,
    ):
        return f"""
            *{{
                color: {color};
                background: {background};
                font-size: {font_size}px;
                font-family: {font_family};
                font-style: {font_style};
                font-weight: {font_weight};
                border-radius: {border_radius}px;
            }}
        """

    def button_style(  # turns repetitive button stylesheets into one setting, reducing redundancy
        self,
        background,
        hover_background,
        font="Verdana",
        font_size=30,
        color="black",
        hover_color="black"
    ):
        return f"""
            *{{
                background: {background};
                color: {color};
                font-family: '{font}';
                font-size: {font_size}px;
            }}
            *:hover{{
                background: {hover_background};
                color: {hover_color};
            }}
        """
                

class MyFirstWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.game_duration = DEFAULT_GAME_DURATION
        self.mole_count = DEFAULT_MOLE_COUNT
        """
        The variable below is a checker for anything that calls the mole_move functions;
        Once a new game starts, prevents any zombie instances from creating complications, 
        especially ones that require a recursive QTimer.
        """
        self.game_id = 0  
        self.display_time = self.game_duration
        self.countdown_timer = QTimer(self) #display timer
        self.countdown_timer.timeout.connect(self.countdown)

        self.setWindowTitle("Whack a mole")
        self.resize(1000, 1000)
        self.preset_home_menu()  
        self.preset_settings()
        self.preset_game_graphics()

        self.pages = QStackedWidget()  # alternator for game/menu widget

        self.pages.addWidget(self.menu_widget)
        self.pages.addWidget(self.game_widget)
        self.pages.addWidget(self.settings_widget)

        self.setCentralWidget(self.pages)
        self.pages.setCurrentWidget(self.menu_widget)
        
    def preset_home_menu(self):  
        """Pre-loads home menu onto a stackedLayout."""
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
        start_game_button.clicked.connect(self.load_game_instance)
        start_game_button.setStyleSheet(
            self.button_style(
                "lightgreen", 'green', 'Consolas', 
                hover_color="white", border="2px solid 'black'", border_radius=10
            )
        )

        settings_button = QPushButton("Settings")
        settings_button.clicked.connect(self.load_settings)
        settings_button.setStyleSheet(
            self.button_style(
                "#ffc640", '#6e5314', 'Consolas', 
                hover_color="white", border="2px solid 'black'", border_radius=10
            )
        )

        for button in (start_game_button, settings_button):
            button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            button.setMinimumSize(400, 120)
        
        clear_score_button = QPushButton("clear score", parent=self.menu_widget)  # developer function
        clear_score_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))  # developer function
        clear_score_button.setStyleSheet(
            "color: grey; background: white; border: 1px solid black"
        )  # developer function
        clear_score_button.move(20, 10)  # developer function
        clear_score_button.clicked.connect(self.clear_score)  # developer function caller (will be removed later)

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
        self.game_widget = QWidget()  # creates the gameplay widget
        self.game_widget.setStyleSheet("background: #D98324;")

        self.label_layout = QHBoxLayout()
        self.label_layout.setContentsMargins(60, 15, 60, 15)

        self.score_ui = QLabel("Score: 0", alignment=Qt.AlignmentFlag.AlignCenter)  # counter stylesheets
        self.score_ui.setMinimumSize(320, 120)
        self.score_ui.setStyleSheet(
            self.label_style(
                "black",  "white", "2px solid grey",
                10, 40
            )
        )
        self.timer_ui = QLabel(
            f"Time: {self.display_time}s", alignment=Qt.AlignmentFlag.AlignCenter
        )
        self.timer_ui.setMinimumSize(320, 120)
        self.timer_ui.setStyleSheet(
            self.label_style(
                "black",  "white", "2px solid grey",
                10, 40
            )
        )
        self.label_layout.addWidget(
            self.timer_ui, 
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        self.label_layout.addWidget(
            self.score_ui, 
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        self.update_grid_size(grid_size - 3)
     
        self.game_layout = QVBoxLayout(self.game_widget)
        self.game_layout.setContentsMargins(10, 0, 10, 5)
        self.game_layout.addLayout(self.label_layout)
        self.game_layout.addLayout(self.grid_layout)
        self.overlay = EndScreenWidget(  # calls EndScreenWidget class as an object in MyFirstWindow
            self.load_home, 
            self.load_game_instance, 
            self.game_widget
        )

        self.mole_queue = []  # list that contains the id of each mole

    def preset_settings(self):
        self.settings_widget = QWidget()
        self.settings_widget.setStyleSheet("background: green")

        st_layout = QVBoxLayout(self.settings_widget)
        slider_layout = QHBoxLayout()
        grid_setting_layout = QHBoxLayout()

        return_button = QPushButton("Return")
        return_button.clicked.connect(self.load_home)
        return_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        return_button.setStyleSheet(
            self.button_style(
                "white", 
                size=40, 
                color="black", 
                border="1px solid black"
            )
        )

        self.input_mole_count = QLineEdit()
        self.input_mole_count.setPlaceholderText("Change mole count here.")
        self.input_mole_count.returnPressed.connect(self.change_mole_count)
        self.input_mole_count.setStyleSheet(
            self.label_style(
                None,
                None,
                "2px solid 'lightgreen'",
                20,
                40
            )
        )

        display_grid_setting = QLabel(
            "Grid Layout", 
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        display_grid_setting.setStyleSheet(
            self.label_style(
                "black",
                "White",
                "2px solid 'darkgreen'",
                20,
                30
            )
        )

        self.set_grid_size = QComboBox() #dropdown menu for {variable name}
        self.set_grid_size.addItems(["3x3", "4x4", "5x5"])
        self.set_grid_size.setCurrentIndex(grid_size - 3) #3x3 grid size is index 0, 4x4 is 1, etc. ^^^^                
        self.set_grid_size.currentIndexChanged.connect(self.update_grid_size) 
        self.set_grid_size.setStyleSheet("""
            font-size: 40px;
            font-family: 'Times New Roman';
            color: black;
            background: white;
        """)

        self.display_game_duration = QLabel(
            f"Game Duration: {self.game_duration}s"
        )
        self.display_game_duration.setMinimumSize(300, 50)
        self.display_game_duration.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display_game_duration.setStyleSheet("""
            font-size: 30px;
            color: black;
            border: 2px solid 'darkgreen';
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

        grid_setting_layout.addWidget(display_grid_setting, stretch=1)
        grid_setting_layout.addWidget(self.set_grid_size, stretch=5)

        slider_layout.addWidget(set_game_time)
        slider_layout.addSpacing(20)
        slider_layout.addWidget(self.display_game_duration)
        slider_layout.setContentsMargins(40, 0, 40, 0)

        st_layout.addWidget(return_button, alignment=Qt.AlignmentFlag.AlignCenter)
        st_layout.addWidget(self.input_mole_count)
        st_layout.addSpacing(200)
        st_layout.addLayout(grid_setting_layout)
        st_layout.addSpacing(200)
        st_layout.addLayout(slider_layout)
        st_layout.setContentsMargins(50, 50, 50, 150)

    def update_grid_size(self, index):
        """
        Three things this function does.
        1. Creates the grid layout on initialization.
        2. Updates grid size (UI/value) directly 
        when the player-selected dropdown menu fires a signal.
        3. If the updated grid size was smaller than the old grid size, 
        automatically reduces mole_count to a number.
        within the boundary of total holes to prevent Overflow that crashes the game.
        """
        global grid_size
        grid_size = index + 3
        total_holes = grid_size ** 2
        if self.mole_count >= total_holes:
            self.mole_count = total_holes - 1
            self.input_mole_count.setPlaceholderText(
                f"Changed mole count to {self.mole_count}"
            )

        if not hasattr(self, "grid_layout"): #creates grid layout once and only once
            self.grid_layout = QGridLayout()
            self.grid_layout.setSpacing(6)
        else:
            # Remove old buttons before creating new grid
            while self.grid_layout.count():
                item = self.grid_layout.takeAt(0)
                button = item.widget()

                if button is not None:
                    button.deleteLater()

        self.buttons = []
        # creates a grid_size x grid_size grid of clickable holes, giving equal space
        for row in range(grid_size): 
            self.grid_layout.setRowStretch(row, 1)
            for col in range(grid_size):
                if row != 0:  # stretches every but the first row
                    self.grid_layout.setColumnStretch(col, 1)
            
                button = QPushButton("")
                button.setMinimumSize(0, 0)
                button.setSizePolicy(
                    QSizePolicy.Policy.Expanding,
                    QSizePolicy.Policy.Expanding
                )
                button.setStyleSheet(self.mole_hole_style())
                button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                self.grid_layout.addWidget(button, row, col)
                # stores created button instances into an array so it can be checked later
                self.buttons.append(button)
                button.clicked.connect(self.whack)  # detects button click and calls whack function
        print(f"Grid size set to {grid_size}x{grid_size}")

    def change_game_duration(self, value):
        self.game_duration = value
        self.display_game_duration.setText(
            f"Game duration: {value}s"
        )

    def change_mole_count(self):
        global grid_size
        try:
            value = int(self.input_mole_count.text())
            self.input_mole_count.clear()
            if value <= 0:
                self.input_mole_count.setPlaceholderText(
                    "Moles must be a positive integer."
                )
            elif value >= (grid_size ** 2):
                self.input_mole_count.setPlaceholderText(
                    f"Moles must be at least one less than total holes ({grid_size ** 2})."
                )
            else:
                self.mole_count = value
                self.input_mole_count.setPlaceholderText(
                    f"Changed mole count to {value}"
                )
        except ValueError:
            self.input_mole_count.clear()
            self.input_mole_count.setPlaceholderText("Invalid integer")

    def mole_hole_style(self):
        radius = min(84, 336 // grid_size)
        font_size = max(16, 160 // grid_size)

        return f"""
            background: #291528;
            border-radius: {radius}px;
            border: 7px solid #DFE0F2;
            color: white;
            font-size: {font_size}px;
        """
    def button_style(  
        self,
        background,
        hover_background=None,
        font="Verdana",
        size=30,
        color="black",
        hover_color=None,
        border=None,
        border_radius=0
    ):
        """
        Turning all styling into one function setting reduces redundancy.
        """
        if hover_background is None:
            hover_background = background

        if hover_color is None:
            hover_color = color

        return f"""
            *{{
                background: {background};
                color: {color};
                font-family: '{font}';
                font-size: {size}px;
                border: {border};
                border-radius: {border_radius}px;
            }}
            *:hover{{
                background: {hover_background};
                color: {hover_color};
            }}
        """

    def label_style( 
        self,
        color,
        background,
        border,
        border_radius,
        font_size,
        font_family="'Times New Roman'",
        font_style=None,
        font_weight=None,
    ):
        """A separate styling function for labels without formatting hover."""
        return f"""
            *{{
                color: {color};
                background: {background};
                font-size: {font_size}px;
                font-family: {font_family};
                border: {border};
                font-style: {font_style};
                font-weight: {font_weight};
                border-radius: {border_radius}px;
            }}
        """

    def load_home(self):
        self.overlay.hide()
        self.pages.setCurrentWidget(self.menu_widget)

    def load_settings(self): 
        self.overlay.hide()
        self.input_mole_count.setPlaceholderText("Change mole count here.")  # refreshes upon each entry 
        self.pages.setCurrentWidget(self.settings_widget)

    def load_game_instance(self):  # triggered by events only, reducing background processing
        # invalidate previous game callbacks, reset the board, score, and moles
        self.game_id += 1
        self.clear_all_moles()

        self.total_mole_movements = 0  # counts the total potential points in any single game
        self.successful_hits = 0
        self.score_ui.setText(f"Score: {self.successful_hits}")
        self.display_time = self.game_duration
        self.timer_ui.setText("Get Ready")

        self.pages.setCurrentWidget(self.game_widget)  # puts the gameplay screen on the main window
        self.overlay.hide()
        
        QTimer.singleShot(0, self.resize_overlay)

        self.now = datetime.now().strftime("%d/%m/%Y, %I:%M %p")
        QTimer.singleShot(2000, self.run_game_instance)  # runs game instance after 2 seconds

    def resize_overlay(self):  # helper function because the overlay QLabel's size is janky when first loaded
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

    def run_game_instance(self):  # starts game, initiates moles, spawns a mole per mole count every 
        self.timer_ui.setText(f"Time: {self.game_duration}s")
        
        self.mole_queue = [] 
        if len(self.mole_queue) == 0:  # check for an empty list before actually appending moles else they duplicate
            for i in range(self.mole_count):
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
        When the mole is whacked, handles score updates and also resets mole_move().
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

    def whack_effect(self, button, is_hit=False):
        """Performs click animation corresponding to whack()."""  
        original_style = button.styleSheet()  # temporary file that stores stylesheet string
        border = "10px solid #39fc03" if is_hit else "9px solid #DFE0F2"
        button.setStyleSheet(f"{original_style}border: {border};")
        temp_file = button.styleSheet()
        QTimer.singleShot(
            75, 
            lambda: button.setStyleSheet(
                temp_file + "border: 7px solid #DFE0F2;"
            )
        )

    def start_next(self):  
        """
        Prepares next mole appearing during start up 
        if max mole count has not been reached.
        """
        if self.mole_index < len(self.mole_queue):
            delay = random.randint(1, 4) * 250
            self.spawn_timer.start(delay)

    def next_mole(self):  
        """Calls for next mole if max mole hasn't been reached."""
        mole_num = self.mole_queue[self.mole_index]

        self.create_moles(mole_num)

        self.mole_index += 1
        self.start_next()
        
    def create_moles(self, mole_num):
        """
        Displays mole text on the board, terminates once max moles have been reached
        """
        empty_buttons = [button for button in self.buttons if button.text() == ""]  # vacancy condition for spawning a mole

        if empty_buttons:  # checks for a vacant button to place the mole
            vacancy = random.choice(empty_buttons)  # picks a random valid location to spawn the mole
            vacancy.setText(mole_num)

            print(f"Created {mole_num}")  # this is for debugging

        move_time = random.randint(mole_speed_min, mole_speed_max)
        current_game = self.game_id
        QTimer.singleShot(
            move_time, 
            lambda: self.mole_move(
                vacancy, 
                mole_num, 
                current_game
            )
        ) # code for forcing mole to move after a set time
        
    def mole_move(self, button, which_mole, game_id):
        """Controls each and every mole separately, through which_mole."""  
        if game_id != self.game_id:  # ignore delayed callbacks to an older game
            return

        if button.text() != which_mole: #stop & reset the move timer if this mole has been hit and moved forcibly
            return
        
        empty_buttons = [
            bt for bt in self.buttons 
            if bt.text() == ""
            ]  # checks for all empty locations that a mole can move to

        move_time = random.randint(mole_speed_min, mole_speed_max)
        
        if empty_buttons: 
            button.setText("") 
            vacancy = random.choice(empty_buttons)  # checks for a vacant button to move the mole
            vacancy.setText(which_mole)
            self.total_mole_movements += 1  # adds a count to total potential points

            current_game = self.game_id

            QTimer.singleShot( # fires recursive function once a mole has moved, cycling endlessly until the timer hits 0.
                move_time,
                lambda: self.mole_move(vacancy, which_mole, current_game) 
            )

    def end_game_instance(self):
        self.spawn_timer.stop()
        self.clear_all_moles()
        self.assess_score()
        self.evaluate_rank()
        self.append_score()
        self.toggle_endscreen()

    def toggle_endscreen(self):
        self.overlay.label.setText(f"Rank: {self.rank}")
        self.overlay.score_label.setText(f"Score: {self.successful_hits}")

        if self.overlay.isVisible():
            self.overlay.hide()
        else:
            """
            When the game ends, the screen instantly pops up, and if the player was clicking the wrong area,
            they could undesirably exit the endscreen, so both buttons are locked for 0.75 seconds on show
            to give them enough reaction time.
            """
            self.overlay.again_button.setDisabled(True) 
            self.overlay.home_button.setDisabled(True)  
            self.overlay.show()
            QTimer.singleShot(750, lambda: self.overlay.again_button.setDisabled(False)) 
            QTimer.singleShot(750, lambda: self.overlay.home_button.setDisabled(False)) 

    def clear_all_moles(self):
        for button in self.buttons:
            button.setText("")

    def assess_score(self):  
        """
        Score accuracy is based off hits over hits + misses (total_mole_movements). A miss is counted when 
            1. A mole moves after not immediately being hit 
            2. The player hits an empty hole
        It is imperative that the player does not click blindly;
        """  
        if self.total_mole_movements == 0: #prevents ZeroDivisionError from ever occurring
            self.accuracy = -1
            self.misses = 0
            return

        self.accuracy = (self.successful_hits / self.total_mole_movements) * 100

        self.misses = self.total_mole_movements - self.successful_hits

    def evaluate_rank(self):
        """Evaluates final rank based on accuracy."""
        if self.accuracy >= 95:
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
        result = (
            f"Game Instance created: {self.now};\\n"
            f"Finished in {self.game_duration} seconds;\\n"
            f"Score: {self.successful_hits};\\n"
            f"Misses: {self.misses};\\n"
            f"Accuracy: {round(self.accuracy, 1)}%;\\n"
            f"Rank: {self.rank}\\n\\n"
        ) 
        # debugging #
        print(result, end="")
        # debugging #    
        with open("score.txt", "a", encoding="utf-8") as file: 
            #only records score when player actually finishes a game without exiting
            file.write(result)

    def clear_score(self): #developer function (will be removed later)
        with open("score.txt", "w", encoding="utf-8"):
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
