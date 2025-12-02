from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QStackedWidget, QMenuBar, QAction, QSplitter)
from PyQt5.QtCore import Qt, QPropertyAnimation, QRect
from src.ui.dashboard_page import DashboardPage
from src.ui.todo_page import TodoPage
from src.ui.projects_page import ProjectsPage
from src.ui.future_plans_page import FuturePlansPage
from src.ui.chatbot_panel import ChatbotPanel
from src.core.router import Router

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HACKER_OS_V1.0")
        self.resize(1200, 800)
        
        # Load Stylesheet
        with open("src/ui/styles/hacker.qss", "r") as f:
            self.setStyleSheet(f.read())
            
        # Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Chatbot Panel (Hidden by default or collapsed)
        self.chatbot = ChatbotPanel()
        self.chatbot.hide() # Start hidden
        
        # Main Content Stack
        self.stack = QStackedWidget()
        self.pages = {
            "DASHBOARD": DashboardPage(),
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
            ("TASKS", "TODO"),
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

    def switch_page(self, page_name):
        if page_name in self.pages:
            self.stack.setCurrentWidget(self.pages[page_name])

    def toggle_chatbot(self):
        if self.chatbot.isVisible():
            self.chatbot.hide()
        else:
            self.chatbot.show()
