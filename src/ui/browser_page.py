from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLineEdit, 
                             QPushButton, QLabel, QFrame, QTabWidget, QTabBar)
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl, Qt

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
        self.back_btn.setFixedWidth(30)
        self.back_btn.clicked.connect(self.go_back)
        
        self.fwd_btn = QPushButton(">")
        self.fwd_btn.setFixedWidth(30)
        self.fwd_btn.clicked.connect(self.go_forward)
        
        self.reload_btn = QPushButton("R")
        self.reload_btn.setFixedWidth(30)
        self.reload_btn.clicked.connect(self.reload_page)
        
        self.url_bar = QLineEdit()
        self.url_bar.setPlaceholderText("ENTER URL...")
        self.url_bar.setStyleSheet("font-family: 'Consolas'; color: #00FF00; background: #000; border: 1px solid #003300; padding: 5px;")
        self.url_bar.returnPressed.connect(self.navigate_to_url)
        
        self.new_tab_btn = QPushButton("+")
        self.new_tab_btn.setFixedWidth(30)
        self.new_tab_btn.clicked.connect(lambda: self.add_new_tab())
        
        nav_layout.addWidget(self.back_btn)
        nav_layout.addWidget(self.fwd_btn)
        nav_layout.addWidget(self.reload_btn)
        nav_layout.addWidget(self.url_bar)
        nav_layout.addWidget(self.new_tab_btn)
        
        layout.addWidget(nav_bar)
        
        # Tab Widget
        self.tabs = QTabWidget()
        self.tabs.setDocumentMode(True)
        self.tabs.setTabsClosable(True)
        self.tabs.tabCloseRequested.connect(self.close_tab)
        self.tabs.currentChanged.connect(self.update_url_bar)
        
        # Style the tabs
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 0; }
            QTabBar::tab { background: #111; color: #888; padding: 8px; border-right: 1px solid #333; }
            QTabBar::tab:selected { background: #222; color: #00FF00; border-bottom: 2px solid #00FF00; }
            QTabBar::close-button { subcontrol-position: right; }
        """)
        
        layout.addWidget(self.tabs)
        
        # Add initial tab
        self.add_new_tab("https://www.google.com")
        
    def add_new_tab(self, url="https://www.google.com"):
        browser = QWebEngineView()
        browser.setUrl(QUrl(url))
        browser.urlChanged.connect(lambda q, b=browser: self.update_tab_title(b, q))
        
        # Inject Dark Mode CSS (Simple invert for now, or custom user script)
        # For a true hacker feel, we might want to invert colors.
        # browser.page().runJavaScript(...) 
        
        i = self.tabs.addTab(browser, "Loading...")
        self.tabs.setCurrentIndex(i)
        
    def close_tab(self, index):
        if self.tabs.count() > 1:
            self.tabs.removeTab(index)
            
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
