from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QStackedWidget, QMenuBar, QAction, QLabel, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, QTimer
from datetime import datetime
from src.ui.dashboard_page import DashboardPage
from src.ui.todo_page import TodoPage
from src.ui.projects_page import ProjectsPage
from src.ui.future_plans_page import FuturePlansPage
from src.ui.task_page import TaskPage
from src.ui.chatbot_panel import ChatbotPanel
from src.core.router import Router

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HACKER_OS_V2.0")
        self.resize(1400, 900)
        
        # Load Stylesheet
        with open("src/ui/styles/hacker.qss", "r") as f:
            self.setStyleSheet(f.read())
            
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Chatbot Panel
        self.chatbot = ChatbotPanel()
        self.chatbot.hide()
        
        # Main Content Stack
        self.stack = QStackedWidget()
        self.pages = {
            "DASHBOARD": DashboardPage(),
            "HABITS": TaskPage(),
            "TODO": TodoPage(),
            "PROJECTS": ProjectsPage(),
            "PLANS": FuturePlansPage()
        }
        
        for name, page in self.pages.items():
            self.stack.addWidget(page)
            
        # Layout Assembly
        main_layout.addWidget(self.chatbot)
        main_layout.addWidget(self.stack)
        
        # Menu Bar
        self.create_menu()
        
        # Router
        Router.instance().navigate_signal.connect(self.switch_page)

    def create_menu(self):
        menubar = self.menuBar()
        
        # Navigation
        nav_menu = menubar.addMenu("NAVIGATION")
        
        actions = [
            ("DASHBOARD", "DASHBOARD"),
            ("HABIT TRACKER", "HABITS"),
            # ("TASKS", "TODO"), # Removed as requested
            ("PROJECTS", "PROJECTS"),
            ("STRATEGY", "PLANS")
        ]
        
        for label, page_key in actions:
            action = QAction(label, self)
            action.triggered.connect(lambda checked, k=page_key: self.switch_page(k))
            nav_menu.addAction(action)
            
        # Tools
        tools_menu = menubar.addMenu("TOOLS")
        chat_action = QAction("TOGGLE_AI_UPLINK", self)
        chat_action.setShortcut("Ctrl+`")
        chat_action.triggered.connect(self.toggle_chatbot)
        tools_menu.addAction(chat_action)
        
        exit_action = QAction("SHUTDOWN", self)
        exit_action.triggered.connect(self.close)
        menubar.addAction(exit_action)
        
        # Top Right Clock (Using a corner widget in menu bar)
        self.clock_lbl = QLabel()
        self.clock_lbl.setStyleSheet("font-family: 'Frozen Crystal Condensed', 'Consolas'; color: #00FF00; font-weight: bold; padding-right: 20px; font-size: 18px;")
        
        # Create a container for the clock to add to the menu bar
        corner_widget = QWidget()
        corner_layout = QHBoxLayout(corner_widget)
        corner_layout.setContentsMargins(0, 0, 0, 0)
        corner_layout.addStretch()
        corner_layout.addWidget(self.clock_lbl)
        
        menubar.setCornerWidget(corner_widget, Qt.TopRightCorner)
        
        # Timer for clock
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_clock)
        self.timer.start(1000)
        self.update_clock()

    def update_clock(self):
        self.clock_lbl.setText(datetime.now().strftime("%A %Y-%m-%d %H:%M:%S"))

    def switch_page(self, page_name):
        if page_name in self.pages:
            self.stack.setCurrentWidget(self.pages[page_name])

    def toggle_chatbot(self):
        if self.chatbot.isVisible():
            self.chatbot.hide()
        else:
            self.chatbot.show()
