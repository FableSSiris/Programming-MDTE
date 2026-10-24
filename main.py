"""
Whack-A-Mole game built with PyQt6.
"""

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
DEFAULT_GRID_SIZE = 4  # default 4x4; can be changed to 3x3 or 5x5 in settings
MOLE_SPEED_MIN = 900  # mole moves earliest after this many ms
MOLE_SPEED_MAX = 2000  # mole moves latest after this many ms
DEFAULT_GAME_DURATION = 15  # in seconds
GRID_AREA_SIZE = 800 # px
GRID_SPACING = 10 # px
INDEX_TO_GRID = 3 # converts combo box index 0 - 4 to grid size 3 - 7
REFLEX_WEIGHTING = 0.7 # sets how much scores contribute towards accuracy weight
PRECISION_WEIGHTING = 1 - REFLEX_WEIGHTING # set remaining weight to precision accuracy (missed clicks)
PREPARATION_DELAY = 2000 # milliseconds
END_SCREEN_BUTTON_DELAY = 750 # ms
BUTTON_ANIMATION_DELAY = 75 # ms
MIN_GAME_DURATION = 15 # seconds
MAX_GAME_DURATION = 60 # seconds


class EndScreenWidget(QWidget):
    """Secondary class for Whack A Mole Game. Creates game end screen overlay."""
    def __init__(
        self,
        home_callback,  # calls load_home from main class when triggered
        play_again_callback, # calls start_game from main class when triggered
        parent=None
    ):
        super().__init__(parent)

        self.setObjectName("overlay") # used for when class is called in WhackAMoleWindow
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
        endscreen_layout = QVBoxLayout(self)
        endscreen_layout.setSpacing(0)
        button_layout = QHBoxLayout()
        button_layout.setSpacing(12)

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

        endscreen_layout.addWidget(
            self.label,
            alignment=Qt.AlignmentFlag.AlignTop
        )
        endscreen_layout.addWidget(
            self.score_label,
            alignment=Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignCenter
        )
        endscreen_layout.addSpacing(50)
        endscreen_layout.addLayout(button_layout)

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
        """Styling function reduces repeated code."""
        return f"""
            QLabel {{
                color: {color};
                background: {background};
                font-size: {font_size}px;
                font-family: {font_family};
                font-style: {font_style};
                font-weight: {font_weight};
                border-radius: {border_radius}px;
            }}
        """

    def button_style(
        self,
        background,
        hover_background,
        font="Verdana",
        font_size=30,
        color="black",
        hover_color="black"
    ):
        """Styling function reduces repeated code."""
        return f"""
            QPushButton {{
                background: {background};
                color: {color};
                font-family: '{font}';
                font-size: {font_size}px;
            }}
            QPushButton:hover{{
                background: {hover_background};
                color: {hover_color};
            }}
        """


class WhackAMoleWindow(QMainWindow):
    """Main Class For Whack A Mole Game."""
    def __init__(self):
        super().__init__()
        self.game_duration = DEFAULT_GAME_DURATION
        self.mole_count = DEFAULT_MOLE_COUNT
        self.grid_size = DEFAULT_GRID_SIZE
        # Below variables are defined inside __init__ first to prevent attribute errors.
        self.hole_size = None # becomes a derived value later
        self.buttons = []
        self.composite_accuracy = 0
        self.mole_missed = 0
        self.empty_hits = 0
        self.successful_hits = 0
        self.now = None # gets datetime in a later function.
        self.mole_queue = []
        self.mole_index = 0
        self.rank = None
        # Checker for anything that calls the create_mole, mole_move, and QTimer functions;
        # Once a new game starts, prevents any zombie callbacks from creating complications
        # especially ones that require a recursive QTimer.
        self.game_id = 0
        #Similar implementation as self.game_id, instead storing individual mole "tokens" that rejects
        #old mole_move() callbacks, ensuring only one timer fires a time, and prevents unpredictable movements.
        self.mole_tokens = {}

        self.display_time = self.game_duration # linked to timer label in gameplay widget
        self.countdown_timer = QTimer(self) # Recursive timer that reduces display time by one every second
        self.countdown_timer.timeout.connect(self.countdown)

        self.spawn_timer = QTimer(self) # Recursive timer that spawns moles on intervals
        self.spawn_timer.setSingleShot(True)
        self.spawn_timer.timeout.connect(self.next_mole)

        self.setWindowTitle("Whack a mole")
        self.resize(1000, 1000)
        self.preset_home_menu()
        self.preset_settings()
        self.preset_game_graphics()

        self.pages = QStackedWidget() # this allows the program to load each widget only once
        self.pages.addWidget(self.menu_widget)
        self.pages.addWidget(self.game_widget)
        self.pages.addWidget(self.settings_widget)

        self.setCentralWidget(self.pages) # Allows Qt to remember every loaded widget at once
        self.pages.setCurrentWidget(self.menu_widget) # this allows switching between them instantly

    def preset_home_menu(self):
        """Pre-loads home widgets, layouts and stylesheets."""
        self.menu_widget = QWidget()
        self.menu_widget.setMinimumSize(1000, 1000)
        self.menu_widget.setStyleSheet("background: #D98324;")

        menu_layout = QVBoxLayout(self.menu_widget)
        menu_layout.setContentsMargins(40, 150, 40, 250)

        menu_title = QLabel("Whack-A-Mole", alignment=Qt.AlignmentFlag.AlignCenter)
        menu_title.setStyleSheet(
            "color: black;"
            "font-size: 80px;"
            "font-family: 'Consolas';"
        )

        start_game_button = QPushButton("Start Game")
        start_game_button.clicked.connect(self.start_game)
        start_game_button.setStyleSheet(
            self.button_style(
                "lightgreen", 'green', 'Consolas',
                hover_color="white", border="2px solid black", border_radius=10
            )
        )

        settings_button = QPushButton("Settings")
        settings_button.clicked.connect(self.load_settings)
        settings_button.setStyleSheet(
            self.button_style(
                "#ffc640", "#6e5314", "Consolas",
                hover_color="white", border="2px solid black", border_radius=10
            )
        )

        for button in (start_game_button, settings_button): # both share the same attributes belows
            button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
            button.setMinimumSize(400, 120)

        menu_layout.addWidget(
            menu_title,
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        menu_layout.addSpacing(70)
        menu_layout.addWidget(
            start_game_button,
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        menu_layout.addSpacing(10)
        menu_layout.addWidget(
            settings_button,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

    def preset_game_graphics(self):
        """Pre-loads game menu widgets, layouts and stylesheets."""
        self.game_widget = QWidget()
        self.game_widget.setStyleSheet("background: #D98324;")

        self.label_layout = QHBoxLayout()
        self.label_layout.setContentsMargins(100, 15, 100, 15)

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
        self.label_layout.setSpacing(0)
        self.label_layout.addWidget(
            self.score_ui,
            alignment=Qt.AlignmentFlag.AlignCenter
        )

        self.grid_container = QWidget() # Keeps button grid centred independent of root layouts
        self.grid_layout = QGridLayout(self.grid_container)
        self.grid_layout.setContentsMargins(0, 0, 0, 0)
        self.grid_layout.setSpacing(GRID_SPACING)
        self.update_grid_size(self.grid_size - INDEX_TO_GRID)  # initial grid layout load

        self.game_layout = QVBoxLayout(self.game_widget)
        self.game_layout.setContentsMargins(0, 0, 0, 20)
        self.game_layout.addLayout(self.label_layout)
        self.game_layout.addWidget(
            self.grid_container, alignment=Qt.AlignmentFlag.AlignCenter
        )
        self.overlay = EndScreenWidget(  # calls EndScreenWidget class as an object in WhackAMoleWindow
            self.load_home,
            self.start_game,
            self.game_widget # so the overlay shows on the correct widget
        )

    def preset_settings(self):
        """Pre-loads settings menu widgets, layouts and stylesheets."""
        self.settings_widget = QWidget()
        self.settings_widget.setStyleSheet("background: green")

        settings_layout = QVBoxLayout(self.settings_widget)
        slider_layout = QHBoxLayout()
        grid_setting_layout = QHBoxLayout()

        return_button = QPushButton("Return")
        return_button.clicked.connect(self.load_home)
        return_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        return_button.setStyleSheet(
            self.button_style(
                "white",
                font_size=40,
                color="black",
                border="1px solid black",
            )
        )

        self.input_mole_count = QLineEdit()
        self.input_mole_count.setPlaceholderText("Change mole count here.")
        self.input_mole_count.returnPressed.connect(self.change_mole_count)
        self.input_mole_count.setStyleSheet("""
            background: #4c4d4c;
            font-family: 'Times New Roman';
            border: 2px solid black;
            border-radius: 20px;
            font-size: 40px;
        """)

        display_grid_setting = QLabel(
            "Grid Layout",
            alignment=Qt.AlignmentFlag.AlignCenter
        )
        display_grid_setting.setStyleSheet(
            self.label_style(
                "black",
                "White",
                "2px solid darkgreen",
                20,
                30
            )
        )

        self.set_grid_size = QComboBox()
        #The grid setup is made to sustain 3x3, 4x4, 5x5
        #But slightly larger dimensions also work
        self.set_grid_size.addItems(
            ["3x3", "4x4", "5x5", "6x6", "7x7"]
        )
        # 3x3 grid size is index 0, 4x4 is 1, etc.
        self.set_grid_size.setCurrentIndex(self.grid_size - INDEX_TO_GRID)
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
        self.display_game_duration.setStyleSheet(
            self.label_style(
                "black", "white", "2px solid darkgreen", 20, 30
            )
        )

        set_game_time = QSlider(Qt.Orientation.Horizontal)
        set_game_time.setRange(MIN_GAME_DURATION, MAX_GAME_DURATION)
        set_game_time.setValue(self.game_duration)
        set_game_time.valueChanged.connect(self.change_game_duration)
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

        self.display_mole_count = QLabel(f"Mole: {self.mole_count}")
        self.display_mole_count.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.display_mole_count.setStyleSheet(
            self.label_style(
                "black", "white", "2px solid darkgreen", 10, 30
            )
        )

        mole_count_layout = QHBoxLayout()
        mole_count_layout.addWidget(self.input_mole_count, stretch=8)
        mole_count_layout.addWidget(self.display_mole_count, stretch=1)

        grid_setting_layout.addWidget(display_grid_setting, stretch=1)
        grid_setting_layout.addWidget(self.set_grid_size, stretch=5)

        slider_layout.addWidget(set_game_time)
        slider_layout.addSpacing(20)
        slider_layout.addWidget(self.display_game_duration)
        slider_layout.setContentsMargins(40, 0, 40, 0)

        settings_layout.addLayout(mole_count_layout)
        settings_layout.addSpacing(200)
        settings_layout.addLayout(grid_setting_layout)
        settings_layout.addSpacing(200)
        settings_layout.addLayout(slider_layout)
        settings_layout.addSpacing(50)
        settings_layout.addWidget(return_button, alignment=Qt.AlignmentFlag.AlignCenter)
        settings_layout.setContentsMargins(50, 50, 50, 150)

    def update_grid_size(self, index):
        """
        Creates the grid layout on initialization.
        Updates its size directly. When needed,
        automatically reduces mole_count to leave
        at least one hole empty.
        """
        self.grid_size = index + INDEX_TO_GRID
        self.hole_size = (
            GRID_AREA_SIZE - (self.grid_size - 1) * GRID_SPACING
        ) // self.grid_size

        total_holes = self.grid_size ** 2
        if self.mole_count >= total_holes:
            self.mole_count = total_holes - 1
            self.input_mole_count.setPlaceholderText(
                f"Changed mole count to {self.mole_count}"
            )
            self.display_mole_count.setText(f"Moles: {self.mole_count}")

        # Remove old buttons before creating new grid
        while self.grid_layout.count():
            item = self.grid_layout.takeAt(0)
            button = item.widget()

            if button is not None:
                button.deleteLater() # gets deleted in the next event loop

        self.buttons = []
        # creates a grid_size x grid_size grid of clickable holes, giving equal space
        for i in range(self.grid_size):
            self.grid_layout.setRowStretch(i, 1)
            self.grid_layout.setColumnStretch(i, 1)
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                button = QPushButton("")
                button.setMinimumSize(int(self.hole_size * 1.5), self.hole_size)
                button.setSizePolicy(
                    QSizePolicy.Policy.Expanding,
                    QSizePolicy.Policy.Expanding
                )
                button.setStyleSheet(self.mole_hole_style())
                button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
                self.grid_layout.addWidget(button, row, col)
                self.buttons.append(button)
                button.clicked.connect(self.whack)
        self.grid_layout.activate()
        self.grid_container.adjustSize() # container accomodates to the button grid instead of otherwise vice versa

    def change_game_duration(self, value):
        """Settings related helper function."""
        self.game_duration = value
        self.display_game_duration.setText(
            f"Game duration: {value}s"
        )

    def change_mole_count(self):
        """
        Changes mole count whilst handling boundary and invalid inputs.
        """
        try:
            value = int(self.input_mole_count.text()) # tries to convert string input into integer
            self.input_mole_count.clear()
            if value <= 0: # if input is non-positive, reject
                self.input_mole_count.setPlaceholderText(
                    "Moles must be a positive integer."
                )
            elif value >= self.grid_size ** 2: # preserves at least one hole for mole movement
                self.input_mole_count.setPlaceholderText(
                    f"Moles must be at least one less than total holes ({self.grid_size ** 2})."
                )
            else: # accepted values
                self.mole_count = value
                self.input_mole_count.setPlaceholderText(
                    f"Changed mole count to {value}"
                )
                self.display_mole_count.setText(f"Mole: {self.mole_count}")
        except ValueError: # Handles non-convertable inputs
            self.input_mole_count.clear()
            self.input_mole_count.setPlaceholderText("Invalid integer")

    def mole_hole_style(self):
        """
        Dynamic stylesheet that changes attributes based on hole geometry.
        """
        radius = self.hole_size // 2
        font_size = max(16, self.hole_size // 4)

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
        font_size=30,
        color="black",
        hover_color=None,
        border="none",
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
            QPushButton{{
                background: {background};
                color: {color};
                font-family: '{font}';
                font-size: {font_size}px;
                border: {border};
                border-radius: {border_radius}px;
            }}
            QPushButton:hover{{
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
        font_style="normal",
        font_weight="normal",
    ):
        """A separate styling function for labels without formatting hover."""
        return f"""
            QLabel {{
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
        """
        Button event-triggered helper function.
        Switches window to home screen.
        """
        self.overlay.hide()
        self.pages.setCurrentWidget(self.menu_widget)

    def load_settings(self):
        """
        Button event-triggered helper function.
        Switches window to settings
        """
        self.overlay.hide()
        self.input_mole_count.setPlaceholderText("Change mole count here.")  # Resets the hint when opening settings
        self.pages.setCurrentWidget(self.settings_widget)

    def start_game(self):
        """
        Invalidate previous game callbacks, reset the board, score, and moles.
        """
        self.game_id += 1
        self.clear_all_moles()
        self.stop_previous_game_timers()

        self.mole_missed = 0
        self.empty_hits = 0
        self.successful_hits = 0
        self.score_ui.setText(f"Score: {self.successful_hits}")
        self.timer_ui.setText("Get Ready")
        self.display_time = self.game_duration

        self.overlay.hide()
        self.pages.setCurrentWidget(self.game_widget)

        #Forces a widget property update or geometry check /after/
        #the layout has finished calculating positions instead of immediately
        QTimer.singleShot(0, self.resize_overlay)

        game_id = self.game_id

        self.now = datetime.now().strftime("%d/%m/%Y, %I:%M %p")
        QTimer.singleShot(
            PREPARATION_DELAY,
            lambda: (
                self.run_game_instance()
                if game_id == self.game_id # avoids stale callback after timer fires
                else None
            )
        )

    def stop_previous_game_timers(self):
        """Stops stale scheduled callbacks."""
        self.countdown_timer.stop()
        self.spawn_timer.stop()

    def resize_overlay(self):
        """Helper that recalculates overlay's geometry on start up and each resizing event."""
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

    def run_game_instance(self):
        """Starts game, initiates moles, spawns a mole sequentially at staggered intervals from existing queue."""
        self.mole_index = 0
        self.mole_queue = [
            f"MOLE{i}" for i in range(self.mole_count)
        ]
        self.mole_tokens = {}

        game_id = self.game_id
        QTimer.singleShot( # game_id check ensures that game instance does not end prematurely
            self.game_duration * 1000,
            lambda: (
                self.end_game_instance() # the program does not currently allow ending a game mid-playing
                if game_id == self.game_id # however, this check opens leeway to future development.
                else None
            )
        )

        self.timer_ui.setText(f"Time: {self.display_time}s")
        self.countdown_timer.start(1000)

        self.start_next()

    def countdown(self):
        """Get live game countdown and display it on self.timer_ui."""
        if self.display_time > 0:
            self.display_time -= 1
            self.timer_ui.setText(f"Time: {self.display_time}s")
        else:
            self.countdown_timer.stop()

    def whack(self):
        """
        Updates score,
        moves a hit mole, reset mole movement, or record an empty click.
        """
        button = self.sender()
        if button.text() != "":
            mole = button.text()
            self.mole_tokens[mole] += 1
            token = self.mole_tokens[mole]

            self.mole_move(
                button, mole, self.game_id, token, is_missed=False
            )
            self.whack_effect(button, is_hit=True)
            self.successful_hits += 1
            self.score_ui.setText(f"Score: {self.successful_hits}")
        else:
            self.empty_hits += 1
            self.whack_effect(button)

    def whack_effect(self, button, is_hit=False):
        """Performs click animation corresponding to whack(). If a mole was inside, changes colour."""
        border_style = "10px solid #39fc03" if is_hit else "9px solid #DFE0F2"

        button.setStyleSheet(
            self.mole_hole_style() + f"""border: {border_style}"""
        )
        QTimer.singleShot(
            BUTTON_ANIMATION_DELAY,
            lambda: button.setStyleSheet(
                self.mole_hole_style()
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
        else:
            self.spawn_timer.stop()

    def next_mole(self):
        """Calls for next mole if max mole hasn't been reached."""
        mole_num = self.mole_queue[self.mole_index]

        self.create_moles(mole_num)

        self.mole_index += 1
        self.start_next()

    def create_moles(self, mole_num):
        """
        Displays mole text on a hole, and schedules its movement.
        """
        empty_buttons = [
            button for button in self.buttons if button.text() == ""
        ]

        if not empty_buttons:
            return # No empty hole to place this mole

        vacancy = random.choice(empty_buttons)
        vacancy.setText(mole_num)
        self.mole_tokens[mole_num] = 0

        move_time = random.randint(MOLE_SPEED_MIN, MOLE_SPEED_MAX)

        game_id = self.game_id
        token = self.mole_tokens[mole_num]

        QTimer.singleShot(
            move_time,
            lambda: self.mole_move(
                vacancy,
                mole_num,
                game_id,
                token
            )
        ) # code for forcing mole to move after a set time

    def mole_move(self, button, which_mole, game_id, token, is_missed=True):
        """
        Moves mole to an empty hole. \n
        The is_missed argument detects a timer-driven mole move and counts it as
        an escape; a player hit passes False.
        """
        if game_id != self.game_id:  # ignore delayed & stale callbacks to an older game
            return

        if button.text() != which_mole: # ignore stale callback
            return

        if token != self.mole_tokens.get(which_mole):
            return

        empty_buttons = [
            btn for btn in self.buttons
            if btn.text() == ""
            ]  # checks for all empty locations that a mole can move to.

        if not empty_buttons:
            # No destination is available for this mole
            return

        move_time = random.randint(MOLE_SPEED_MIN, MOLE_SPEED_MAX)

        button.setText("")
        vacancy = random.choice(empty_buttons)
        vacancy.setText(which_mole)

        if is_missed: # tallys mole move without being hit
            self.mole_missed += 1

        self.mole_tokens[which_mole] += 1
        updated_token = self.mole_tokens[which_mole]

        QTimer.singleShot( # next callback is only valid for this "token" version
            move_time,
            lambda: self.mole_move(
                vacancy, which_mole, game_id, updated_token
            )
        )

    def end_game_instance(self):
        """
        Finalises the game, saves the result, and displays the endscreen.
        """
        self.game_id += 1 # Invalidates old timer callbacks
        self.clear_all_moles()
        self.timer_ui.setText("Time: 0s")
        self.stop_previous_game_timers()

        self.assess_score()
        self.evaluate_rank()
        self.append_score()
        self.show_endscreen()


    def show_endscreen(self):
        self.overlay.label.setText(f"Rank: {self.rank}")
        self.overlay.score_label.setText(f"Score: {self.successful_hits}")

        # briefly disables both buttons to prevent accidental clicks as overlay appears
        self.overlay.again_button.setDisabled(True)
        self.overlay.home_button.setDisabled(True)
        self.overlay.show()

        def enable_buttons():
            self.overlay.again_button.setDisabled(False)
            self.overlay.home_button.setDisabled(False)
        QTimer.singleShot(
            END_SCREEN_BUTTON_DELAY,
            enable_buttons
        )

    def clear_all_moles(self):
        for button in self.buttons:
            button.setText("")

    def assess_score(self):
        """
        Total accuracy is a weighted average of precision and reflex.
        Precision measures hits against all player clicks; reflex measures hit against
        hits and escaped moles.
        Composite Accuracy (%) = hits / clicks * 0.3 + hits / (hits + escaped) * 0.7
        """
        attempts = self.successful_hits + self.empty_hits
        total_mole_movements = self.successful_hits + self.mole_missed

        if total_mole_movements == 0: #prevents ZeroDivisionError
            self.composite_accuracy = -1 # marks -1 if no mole movement occurs.
            return

        if attempts == 0: #prevents second ZeroDivision Error
            precision_accuracy = 0 # Precision is counted as 0 if no hits were attempted
        else:
            precision_accuracy = (self.successful_hits / attempts) * 100

        reflex_accuracy = (self.successful_hits / total_mole_movements) * 100
        self.composite_accuracy = (
            reflex_accuracy * REFLEX_WEIGHTING + precision_accuracy * PRECISION_WEIGHTING
        )

    def evaluate_rank(self):
        """
        Evaluates final rank based on composite accuracy, counting both empty holes and missed moles.\n
        Thresholds: S >= 95%, A >= 80%, B >= 60%, C >= 40%, D >= 10%, F >= 0%
        """
        if self.composite_accuracy >= 95:
            self.rank = "S"
        elif self.composite_accuracy >= 80:
            self.rank = "A"
        elif self.composite_accuracy >= 60:
            self.rank = "B"
        elif self.composite_accuracy >= 40:
            self.rank = "C"
        elif self.composite_accuracy >= 10:
            self.rank = "D"
        elif self.composite_accuracy >= 0:
            self.rank = "F"
        else:
            self.rank = "undefined"

    def append_score(self):
        if self.composite_accuracy == -1: # skips saving result if accuracy is marked instead of calculated
            print("Result was not appended.")
            return
        result = (
            f"Game Instance created: {self.now};\n"
            f"Finished in {self.game_duration} seconds;\n"
            f"Score: {self.successful_hits};\n"
            f"Missed Clicks: {self.empty_hits};\n"
            f"Missed Moles: {self.mole_missed};\n"
            f"Accuracy: {round(self.composite_accuracy, 1)}%;\n"
            f"Rank: {self.rank}\n\n"
        )
        print(result, end="")

        try:
            with open("score.txt", "a", encoding="utf-8") as file:
                # Called only when a game finishes normally
                file.write(result)
        except OSError as error: # handles file access or write failures
            print(f"Could not save score: {error}")

    def resizeEvent(self, event):
        """Recalculates overlay geometry based off window size"""
        super().resizeEvent(event)
        if hasattr(self, "overlay"):
            self.resize_overlay()


app = QApplication(sys.argv)
window = WhackAMoleWindow()
window.show()
sys.exit(app.exec())
