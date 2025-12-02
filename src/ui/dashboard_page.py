from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QGridLayout, QFrame
from PyQt5.QtCore import QTimer, Qt
from datetime import datetime
from src.core.data_manager import DataManager
from src.core.cpp_bridge import CppBridge

class StatCard(QFrame):
    def __init__(self, title, value):
        super().__init__()
        self.setProperty("class", "Card")
        layout = QVBoxLayout(self)
        self.title_lbl = QLabel(title)
        self.title_lbl.setStyleSheet("color: #888; font-size: 12px;")
        self.value_lbl = QLabel(str(value))
        self.value_lbl.setStyleSheet("color: #00FF00; font-size: 24px; font-weight: bold;")
        layout.addWidget(self.title_lbl)
        layout.addWidget(self.value_lbl)

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()
        layout = QVBoxLayout(self)
        
        # Time Display
        self.time_lbl = QLabel()
        self.time_lbl.setAlignment(Qt.AlignCenter)
        self.time_lbl.setStyleSheet("font-size: 48px; color: #00FF00; font-weight: bold;")
        layout.addWidget(self.time_lbl)
        
        # Stats Grid
        stats_layout = QGridLayout()
        self.tasks_card = StatCard("PENDING TASKS", 0)
        self.projects_card = StatCard("ACTIVE PROJECTS", 0)
        self.cpp_card = StatCard("C++ MODULE", "LOADING...")
        
        stats_layout.addWidget(self.tasks_card, 0, 0)
        stats_layout.addWidget(self.projects_card, 0, 1)
        stats_layout.addWidget(self.cpp_card, 0, 2)
        layout.addLayout(stats_layout)
        
        # Matrix Rain / Log Area
        self.log_area = QLabel("SYSTEM LOGS INITIALIZED...")
        self.log_area.setStyleSheet("color: #003300; font-size: 10px; padding: 10px; border: 1px dashed #003300;")
        self.log_area.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.log_area.setWordWrap(True)
        layout.addWidget(self.log_area, stretch=1)
        
        # Timers
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)
        
        self.matrix_timer = QTimer(self)
        self.matrix_timer.timeout.connect(self.update_matrix)
        self.matrix_timer.start(100)
        
        self.update_time()
        self.refresh_stats()

    def update_time(self):
        now = datetime.now()
        self.time_lbl.setText(now.strftime("%H:%M:%S"))
        self.refresh_stats() # Periodically refresh data

    def refresh_stats(self):
        tasks = self.data_manager.get_tasks()
        projects = self.data_manager.get_projects()
        
        pending = sum(1 for t in tasks if not t['completed'])
        self.tasks_card.value_lbl.setText(str(pending))
        self.projects_card.value_lbl.setText(str(len(projects)))
        
        # Check C++ Status
        try:
            # Simple check
            primes = CppBridge.find_primes(10)
            self.cpp_card.value_lbl.setText("ONLINE" if primes else "OFFLINE")
            self.cpp_card.value_lbl.setStyleSheet("color: #00FFFF;" if primes else "color: #FF0000;")
        except:
             self.cpp_card.value_lbl.setText("ERROR")

    def update_matrix(self):
        # Generate a frame of matrix rain using C++ (or fallback)
        rain = CppBridge.generate_matrix_rain(60, 10, int(datetime.now().timestamp()))
        self.log_area.setText(rain)
