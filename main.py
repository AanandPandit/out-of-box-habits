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
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
