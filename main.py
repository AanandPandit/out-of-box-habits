import sys
import os
from PyQt5.QtWidgets import QApplication
from src.ui.main_window import MainWindow

# Ensure src is in path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def main():
    # Set environment variables for high DPI
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    
    app = QApplication(sys.argv)
    
    # Splash Screen
    from src.ui.splash_screen import StartupAnimationWindow
    splash = StartupAnimationWindow()
    
    # Main Window (created but hidden)
    window = MainWindow()
    
    def show_main():
        window.show()
    
    splash.finished.connect(show_main)
    splash.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
