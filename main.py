# main.py
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QPushButton, QStackedWidget, QLabel
)
from PyQt5.QtCore import Qt
from speaker_design import SpeakerDesignStudio

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Maaleh Audio Studio")
        self.resize(800, 600)

        # Stacked widget to hold pages
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # --- Page 1: Initial Menu ---
        menu_page = QWidget()
        # Dark gray background
        menu_page.setStyleSheet("background-color: #171717;")
        menu_layout = QVBoxLayout(menu_page)
        # Center buttons
        menu_layout.setAlignment(Qt.AlignCenter)
        menu_layout.setSpacing(20)

        # Button style
        btn_style = """
            QPushButton {
                background-color: #000;
                color: lightgray;
                border: none;
            }
            QPushButton:hover {
                background-color: #333;
            }
        """

        # Medium-sized buttons
        btn_speaker = QPushButton("Design Speaker")
        btn_speaker.setFixedSize(200, 60)
        btn_speaker.setStyleSheet(btn_style)

        btn_amp = QPushButton("Design Tube Amp")
        btn_amp.setFixedSize(200, 60)
        btn_amp.setStyleSheet(btn_style)

        btn_other = QPushButton("Other")
        btn_other.setFixedSize(200, 60)
        btn_other.setStyleSheet(btn_style)

        # Add buttons to menu
        menu_layout.addWidget(btn_speaker)
        menu_layout.addWidget(btn_amp)
        menu_layout.addWidget(btn_other)
        self.stack.addWidget(menu_page)

        # --- Page 2: Speaker Design ---
        speaker_window = SpeakerDesignStudio()
        speaker_page = speaker_window.centralWidget()
        self.stack.addWidget(speaker_page)

        # --- Page 3: Tube Amp Design (Placeholder) ---
        amp_page = QWidget()
        amp_page.setStyleSheet("background-color: #0e0e0e;")
        amp_layout = QVBoxLayout(amp_page)
        amp_layout.setAlignment(Qt.AlignCenter)
        amp_label = QLabel("Tube Amp Design Coming Soon")
        amp_label.setStyleSheet("color: lightgray;")
        amp_layout.addWidget(amp_label)
        self.stack.addWidget(amp_page)

        # --- Connect Buttons to Pages ---
        btn_speaker.clicked.connect(lambda: self.stack.setCurrentWidget(speaker_page))
        btn_amp.clicked.connect(lambda: self.stack.setCurrentWidget(amp_page))
        btn_other.clicked.connect(lambda: self.stack.setCurrentWidget(menu_page))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
