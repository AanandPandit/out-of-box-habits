from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QScrollArea, 
                             QLabel, QPushButton, QLineEdit, QTextEdit, QFrame, QProgressBar)
from src.core.data_manager import DataManager

class ProjectCard(QFrame):
    def __init__(self, project):
        super().__init__()
        self.setProperty("class", "Card")
        layout = QVBoxLayout(self)
        
        header = QHBoxLayout()
        name = QLabel(project['name'])
        name.setStyleSheet("font-weight: bold; font-size: 16px; color: #00FFFF;")
        header.addWidget(name)
        layout.addLayout(header)
        
        desc = QLabel(project['description'])
        desc.setWordWrap(True)
        layout.addWidget(desc)
        
        prog = QProgressBar()
        prog.setValue(project.get('progress', 0))
        prog.setStyleSheet("QProgressBar { border: 1px solid #003300; text-align: center; } QProgressBar::chunk { background-color: #00FF00; }")
        layout.addWidget(prog)

class ProjectsPage(QWidget):
    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()
        layout = QVBoxLayout(self)
        
        header = QLabel("PROJECT_OVERWATCH")
        header.setObjectName("Header")
        layout.addWidget(header)
        
        # New Project Form
        form_layout = QHBoxLayout()
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("Project Name")
        self.desc_input = QLineEdit()
        self.desc_input.setPlaceholderText("Description")
        self.add_btn = QPushButton("INIT PROJECT")
        self.add_btn.clicked.connect(self.add_project)
        
        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.desc_input)
        form_layout.addWidget(self.add_btn)
        layout.addLayout(form_layout)
        
        # Scroll Area for Cards
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("background: transparent; border: none;")
        
        self.container = QWidget()
        self.container_layout = QVBoxLayout(self.container)
        self.container_layout.addStretch()
        
        scroll.setWidget(self.container)
        layout.addWidget(scroll)
        
        self.refresh_list()

    def add_project(self):
        name = self.name_input.text().strip()
        desc = self.desc_input.text().strip()
        if name:
            self.data_manager.add_project(name, desc)
            self.name_input.clear()
            self.desc_input.clear()
            self.refresh_list()

    def refresh_list(self):
        # Clear existing items (except stretch)
        while self.container_layout.count() > 1:
            item = self.container_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        projects = self.data_manager.get_projects()
        for p in projects:
            card = ProjectCard(p)
            self.container_layout.insertWidget(self.container_layout.count()-1, card)
