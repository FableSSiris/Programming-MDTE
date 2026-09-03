import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget


class MyFirstWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Whack a mole")
        self.setFixedSize(500, 500)

        self.grid_layout = QGridLayout()
        self.buttons = [] #buttons array
        for row in range(4): #creates 4 columns
            self.row_buttons = []
            for col in range(4): #creates a column of 4 buttons
                self.button = QPushButton()
                self.button.setFixedSize(85, 85)
                self.button.setStyleSheet(
                    "background-color: #0f0;"
                    "border-radius: 40;"
                    "border: 7px solid brown"
                    )
                self.grid_layout.addWidget(self.button, row, col)
                self.row_buttons.append(self.button)
                self.button.clicked.connect(lambda clicked, 
                                            r=row, c=col:self.button_clicked(r, c)) #detects button click and calls button_clicked function
            self.buttons.append(self.row_buttons) #puts the created button instances into an array

        self.game_widget = QWidget() #creates the widget for the game
        self.game_widget.setLayout(self.grid_layout)
        self.game_widget.setStyleSheet("background-color: #55a12d")

        self.setCentralWidget(self.game_widget)

    def button_clicked(self, row, col):
        QApplication.quit() #closes the program

app = QApplication(sys.argv)
window = MyFirstWindow() #finalizes the window
window.show()
sys.exit(app.exec())
print('Hello World!')
