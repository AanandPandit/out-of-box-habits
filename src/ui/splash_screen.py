from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QProgressBar, 
                             QGraphicsOpacityEffect, QApplication)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor, QFont

class BootLog(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setAlignment(Qt.AlignLeft | Qt.AlignBottom)
        self.layout.setSpacing(2)
        self.logs = [
            "Initializing system kernel...",
            "Loading AI uplink...",
            "Bypassing firewalls...",
            "Decrypting user data...",
            "Establishing secure connection...",
            "System ready."
        ]
        self.current_log = 0
        
    def add_log(self):
        if self.current_log < len(self.logs):
            lbl = QLabel(f">> {self.logs[self.current_log]}")
            lbl.setStyleSheet("color: #00FF00; font-family: 'Consolas'; font-size: 12px;")
            self.layout.addWidget(lbl)
            self.current_log += 1
            return True
        return False

class StartupAnimationWindow(QWidget):
    finished = pyqtSignal()

    def __init__(self):
        super().__init__()
        
        # Window Setup
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.SplashScreen)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(500, 300)
        self.center_on_screen()
        
        # Main Container (The visible part)
        self.container = QWidget(self)
        self.container.setGeometry(10, 10, 480, 280)
        self.container.setStyleSheet("""
            QWidget {
                background-color: #050505;
                border: 2px solid #00FF00;
                border-radius: 10px;
            }
        """)
        
        layout = QVBoxLayout(self.container)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Logo / Title
        self.title_lbl = QLabel("HACKER_OS v2.0")
        self.title_lbl.setAlignment(Qt.AlignCenter)
        self.title_lbl.setStyleSheet("color: #00FFFF; font-family: 'Consolas'; font-size: 32px; font-weight: bold; border: none;")
        layout.addWidget(self.title_lbl)
        
        layout.addStretch()
        
        # Boot Logs
        self.boot_log = BootLog()
        self.boot_log.setStyleSheet("border: none;")
        layout.addWidget(self.boot_log)
        
        layout.addStretch()
        
        # Progress Bar
        self.progress = QProgressBar()
        self.progress.setTextVisible(False)
        self.progress.setFixedHeight(5)
        self.progress.setStyleSheet("""
            QProgressBar {
                border: 1px solid #333;
                background-color: #111;
                border-radius: 2px;
            }
            QProgressBar::chunk {
                background-color: #00FF00;
            }
        """)
        layout.addWidget(self.progress)
        
        # Timers
        self.progress_val = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_progress)
        self.timer.start(50) # 50ms * 100 = 5000ms (approx 5s total, but we speed up)
        
        self.log_timer = QTimer(self)
        self.log_timer.timeout.connect(self.update_logs)
        self.log_timer.start(600)

    def center_on_screen(self):
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move((screen.width() - size.width()) // 2, (screen.height() - size.height()) // 2)

    def update_progress(self):
        self.progress_val += 1
        self.progress.setValue(self.progress_val)
        
        if self.progress_val >= 100:
            self.timer.stop()
            self.log_timer.stop()
            self.close_animation()

    def update_logs(self):
        self.boot_log.add_log()

    def close_animation(self):
        # Fade out
        self.opacity_effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.opacity_effect)
        
        self.anim = QPropertyAnimation(self.opacity_effect, b"opacity")
        self.anim.setDuration(1000)
        self.anim.setStartValue(1.0)
        self.anim.setEndValue(0.0)
        self.anim.setEasingCurve(QEasingCurve.OutQuad)
        self.anim.finished.connect(self.on_finished)
        self.anim.start()

    def on_finished(self):
        self.close()
        self.finished.emit()

if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    splash = StartupAnimationWindow()
    splash.show()
    sys.exit(app.exec_())
