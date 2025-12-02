from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, 
                             QStackedWidget, QMenuBar, QAction, QLabel, QSpacerItem, QSizePolicy, QSplitter, QLineEdit)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
from datetime import datetime
import requests
import time
from src.ui.dashboard_page import DashboardPage
from src.ui.task_page import TaskPage
from src.ui.browser_page import BrowserPage
from src.ui.chatbot_panel import ChatbotPanel
from src.ui.transition_overlay import TransitionOverlay
from src.core.router import Router

class NetWorker(QThread):
    stats_signal = pyqtSignal(bool, float)
    
    def run(self):
        while True:
            try:
                start = time.time()
                requests.get("https://www.google.com", timeout=2)
                ping = (time.time() - start) * 1000
                self.stats_signal.emit(True, ping)
            except:
                self.stats_signal.emit(False, 0)
            time.sleep(5)

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
        main_layout = QVBoxLayout(central_widget) # Changed to Vertical to accommodate footer
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Content Area (Splitter)
        content_area = QWidget()
        content_layout = QHBoxLayout(content_area)
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        self.splitter = QSplitter(Qt.Horizontal)
        content_layout.addWidget(self.splitter)
        
        # Chatbot Panel
        self.chatbot = ChatbotPanel()
        self.chatbot.hide()
        
        # Main Content Stack
        self.stack = QStackedWidget()
        self.pages = {
            "DASHBOARD": DashboardPage(),
            "HABITS": TaskPage(),
            "BROWSER": BrowserPage()
        }
        
        for name, page in self.pages.items():
            self.stack.addWidget(page)
            
        # Add to Splitter
        self.splitter.addWidget(self.chatbot)
        self.splitter.addWidget(self.stack)
        self.splitter.setSizes([400, 1000])
        self.splitter.setCollapsible(0, True)
        
        main_layout.addWidget(content_area)
        
        # Footer / Command Shell
        footer = QWidget()
        footer.setFixedHeight(40)
        footer.setStyleSheet("background-color: #000; border-top: 1px solid #00FF00;")
        footer_layout = QHBoxLayout(footer)
        footer_layout.setContentsMargins(10, 0, 10, 0)
        
        # Net Stats
        self.net_lbl = QLabel("NET: INITIALIZING...")
        self.net_lbl.setStyleSheet("color: #888; font-family: 'Consolas'; font-size: 12px; margin-right: 15px;")
        footer_layout.addWidget(self.net_lbl)
        
        lbl = QLabel("root@hacker_os:~$")
        lbl.setStyleSheet("color: #00FF00; font-weight: bold;")
        footer_layout.addWidget(lbl)
        
        self.cmd_input = QLineEdit()
        self.cmd_input.setPlaceholderText("Enter command...")
        self.cmd_input.setStyleSheet("background: transparent; border: none; color: #00FFFF; font-family: 'Consolas'; font-size: 14px;")
        self.cmd_input.returnPressed.connect(self.process_command)
        footer_layout.addWidget(self.cmd_input)
        
        main_layout.addWidget(footer)
        
        # Transition Overlay (Floating on top of stack)
        self.overlay = TransitionOverlay(self.stack)
        self.overlay.resize(self.stack.size())
        self.overlay.hide()
        self.overlay.finished.connect(self.on_transition_finished)
        
        # Menu Bar
        self.create_menu()
        
        # Router
        Router.instance().navigate_signal.connect(self.switch_page)
        
        self.pending_page = None
        
        # Start Net Worker
        self.net_worker = NetWorker()
        self.net_worker.stats_signal.connect(self.update_net_stats)
        self.net_worker.start()

    def update_net_stats(self, online, ping):
        if online:
            color = "#00FF00"
            text = f"NET: ONLINE | PING: {int(ping)}ms"
        else:
            color = "#FF0000"
            text = "NET: OFFLINE"
        self.net_lbl.setText(text)
        self.net_lbl.setStyleSheet(f"color: {color}; font-family: 'Consolas'; font-size: 12px; margin-right: 15px;")

    def resizeEvent(self, event):
        self.overlay.resize(self.stack.size())
        super().resizeEvent(event)

    def process_command(self):
        cmd = self.cmd_input.text().strip().lower()
        self.cmd_input.clear()
        
        if cmd in ["dash", "dashboard", "home"]:
            self.switch_page("DASHBOARD")
        elif cmd in ["habits", "tasks", "tracker"]:
            self.switch_page("HABITS")
        elif cmd in ["web", "browser", "net"]:
            self.switch_page("BROWSER")
        elif cmd in ["chat", "ai", "uplink"]:
            self.toggle_chatbot()
        elif cmd.startswith("open "):
            # Open URL in browser
            target = cmd.split(" ", 1)[1]
            url = target
            if target == "youtube": url = "https://www.youtube.com"
            elif target == "google": url = "https://www.google.com"
            elif target == "github": url = "https://www.github.com"
            elif target == "reddit": url = "https://www.reddit.com"
            
            self.switch_page("BROWSER")
            self.pages["BROWSER"].add_new_tab(url)
        elif cmd == "exit":
            self.close()
            
    def switch_page(self, page_name):
        if page_name in self.pages and self.stack.currentWidget() != self.pages[page_name]:
            self.pending_page = self.pages[page_name]
            # Start Animation
            self.overlay.raise_()
            self.overlay.start_animation(f"ACCESSING {page_name}...")
            
    def on_transition_finished(self):
        if self.pending_page:
            self.stack.setCurrentWidget(self.pending_page)
            self.pending_page = None

    def create_menu(self):
        menubar = self.menuBar()
        
        # Dashboard
        dash_action = QAction("DASHBOARD", self)
        dash_action.triggered.connect(lambda: self.switch_page("DASHBOARD"))
        menubar.addAction(dash_action)
        
        # Habits Manager (Top Level)
        habits_action = QAction("HABITS MANAGER", self)
        habits_action.triggered.connect(lambda: self.switch_page("HABITS"))
        menubar.addAction(habits_action)
        
        # Browser (Top Level)
        browser_action = QAction("BROWSER", self)
        browser_action.triggered.connect(lambda: self.switch_page("BROWSER"))
        menubar.addAction(browser_action)
            
        # Chat Toggle (Directly in menu bar)
        chat_action = QAction("CHAT_UPLINK", self)
        chat_action.setShortcut("Ctrl+`")
        chat_action.triggered.connect(self.toggle_chatbot)
        menubar.addAction(chat_action)
        
        # Top Right Clock (Using a corner widget in menu bar)
        self.clock_lbl = QLabel()
        self.clock_lbl.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        # Updated font to "Technology" as requested
        self.clock_lbl.setStyleSheet("font-family: 'Technology', 'Consolas'; font-weight: bold; padding-right: 20px;")
        
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
        # Time on line 1 (Large Green), Date + Day on line 2 (Small Grey)
        now = datetime.now()
        time_str = now.strftime("%H:%M:%S")
        
        # Use HTML for multi-color/size
        html = f"""
        <div style='text-align: right;'>
            <span style='font-size: 24px; color: #888888;'>{time_str}</span>
        </div>
        """
        self.clock_lbl.setText(html)

    def toggle_chatbot(self):
        if self.chatbot.isVisible():
            self.chatbot.hide()
        else:
            self.chatbot.show()
