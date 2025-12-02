from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QLabel, QFrame, QTabWidget, QTabBar)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt, QSize

class BrowserPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Navigation Bar
        nav_bar = QFrame()
        nav_bar.setStyleSheet("background-color: #050505; border-bottom: 1px solid #00FF00;")
        nav_layout = QHBoxLayout(nav_bar)
        nav_layout.setContentsMargins(5, 5, 5, 5)
        
        self.back_btn = QPushButton("<")
        self.back_btn.setFixedSize(40, 40)
        self.back_btn.setStyleSheet("font-size: 20px; font-weight: bold; border: 1px solid #00FF00; color: #00FF00; background: #000;")
        self.back_btn.clicked.connect(self.go_back)
        
        self.fwd_btn = QPushButton(">")
        self.fwd_btn.setFixedSize(40, 40)
        self.fwd_btn.setStyleSheet("font-size: 20px; font-weight: bold; border: 1px solid #00FF00; color: #00FF00; background: #000;")
        self.fwd_btn.clicked.connect(self.go_forward)
        
        self.reload_btn = QPushButton("R")
        self.reload_btn.setFixedSize(40, 40)
        self.reload_btn.setStyleSheet("font-size: 20px; font-weight: bold; border: 1px solid #00FF00; color: #00FF00; background: #000;")
        self.reload_btn.clicked.connect(self.reload_page)
        
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("ENTER URL...")
        self.url_bar.setStyleSheet("font-family: 'Consolas'; font-size: 16px; color: #00FF00; background: #000; border: 1px solid #003300; padding: 10px;")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        
        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.fwd_btn)
        nav_layout.addWidget(self.reload_btn)
        nav_layout.addWidget(self.url_bar)
        
        layout.addWidget(nav_bar)
        
        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(False) # We will use custom buttons
        self.tabs.currentChanged.connect(self.update_url_bar)
        
        # New Tab Button in Corner
        self.new_tab_btn = QPushButton("+")
        self.new_tab_btn.setFixedSize(40, 40)
        self.new_tab_btn.setStyleSheet("font-size: 24px; font-weight: bold; border: none; color: #00FF00; background: transparent;")
        self.new_tab_btn.clicked.connect(lambda: self.add_new_tab())
        self.tabs.setCornerWidget(self.new_tab_btn, Qt.TopRightCorner)
        
        # Style the tabs
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 0; background: #000; }
            QTabBar::tab { background: #111; color: #888; padding: 10px 20px; border-right: 1px solid #333; font-size: 14px; }
            QTabBar::tab:selected { background: #222; color: #00FF00; border-bottom: 2px solid #00FF00; }
        """)
        
        layout.addWidget(self.tabs)
        
        # Add initial tab
        self.add_new_tab("https://www.google.com")
        
    def add_new_tab(self, url="https://www.google.com"):
        browser = QWebEngineView()
        browser.setStyleSheet("background-color: #222;") # Set background to avoid white flash
        browser.setUrl(QUrl(url))
        browser.urlChanged.connect(lambda q, b=browser: self.update_tab_title(b, q))
        browser.loadFinished.connect(lambda _, b=browser: b.show()) # Ensure show is called after load
        
        i = self.tabs.addTab(browser, "Loading...")
        self.tabs.setCurrentIndex(i)
        
        # Add Custom Close Button "x"
        close_btn = QPushButton("x")
        close_btn.setFixedSize(20, 20)
        close_btn.setStyleSheet("""
            QPushButton { border: none; color: #888; font-weight: bold; background: transparent; }
            QPushButton:hover { color: #FF0000; }
        """)
        close_btn.clicked.connect(lambda _, index=i: self.close_tab(index))
        self.tabs.tabBar().setTabButton(i, QTabBar.RightSide, close_btn)
        
    def close_tab(self, index):
        # The index might shift if tabs are closed, so we need to be careful.
        # But since we bind the index at creation, it might be stale.
        # Better to find the widget and remove it.
        # However, QTabBar doesn't easily give us the widget from the button click without some work.
        # Let's try to find the index dynamically based on the sender? 
        # Actually, simpler: The lambda captures 'i' by value at creation. 
        # If we close tab 0, tab 1 becomes tab 0. The button on old tab 1 still thinks it's index 1.
        # So we need a robust way.
        
        # Robust way: Iterate tabs and check which one has the sender as the button.
        sender = self.sender()
        for i in range(self.tabs.count()):
            btn = self.tabs.tabBar().tabButton(i, QTabBar.RightSide)
            if btn == sender:
                self.tabs.removeTab(i)
                return

    def update_tab_title(self, browser, url):
        index = self.tabs.indexOf(browser)
        if index != -1:
            title = browser.title()
            if len(title) > 15: title = title[:15] + "..."
            self.tabs.setTabText(index, title)
        
        if browser == self.tabs.currentWidget():
            self.update_url_bar()
            
    def navigate_to_url(self):
        url = self.url_bar.text().strip()
        if not url.startswith("http"):
            url = "https://" + url
        
        if self.tabs.currentWidget():
            self.tabs.currentWidget().setUrl(QUrl(url))
        
    def update_url_bar(self):
        if self.tabs.currentWidget():
            url = self.tabs.currentWidget().url().toString()
            self.url_bar.setText(url)
            
    def go_back(self):
        if self.tabs.currentWidget():
            self.tabs.currentWidget().back()
            
    def go_forward(self):
        if self.tabs.currentWidget():
            self.tabs.currentWidget().forward()
            
    def reload_page(self):
        if self.tabs.currentWidget():
            self.tabs.currentWidget().reload()
