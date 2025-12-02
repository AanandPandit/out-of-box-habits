from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
import random

class TransitionOverlay(QWidget):
    finished = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 240);")
        self.setAttribute(Qt.WA_TransparentForMouseEvents, False) # Block mouse events
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)
        
        self.label = QLabel("")
        self.label.setStyleSheet("color: #00FF00; font-family: 'Consolas'; font-size: 48px; font-weight: bold;")
        self.label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.label)
        
        self.target_text = ""
        self.current_text = ""
        self.chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,.<>?"
        self.steps = 0
        self.max_steps = 20
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_animation)

    def start_animation(self, target_text):
        self.target_text = target_text
        self.steps = 0
        self.show()
        self.raise_()
        self.timer.start(30) # 30ms per frame

    def update_animation(self):
        if self.steps >= self.max_steps:
            self.label.setText(self.target_text)
            self.timer.stop()
            QTimer.singleShot(200, self.finish) # Hold for a moment
            return

        # Decoding effect
        display_text = ""
        for i in range(len(self.target_text)):
            if i < (self.steps / self.max_steps) * len(self.target_text):
                display_text += self.target_text[i]
            else:
                display_text += random.choice(self.chars)
        
        self.label.setText(display_text)
        self.steps += 1

    def finish(self):
        self.hide()
        self.finished.emit()
