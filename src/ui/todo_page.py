from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QListWidget, 
                             QListWidgetItem, QLineEdit, QPushButton, QCheckBox, QLabel)
from PyQt5.QtCore import Qt
from src.core.data_manager import DataManager

class TodoPage(QWidget):
    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()
        layout = QVBoxLayout(self)
        
        header = QLabel("TASK_MANAGER_V1.0")
        header.setObjectName("Header")
        layout.addWidget(header)
        
        # Input
        input_layout = QHBoxLayout()
        self.task_input = QLineEdit()
        self.task_input.setPlaceholderText("New objective...")
        self.add_btn = QPushButton("ADD")
        self.add_btn.clicked.connect(self.add_task)
        
        input_layout.addWidget(self.task_input)
        input_layout.addWidget(self.add_btn)
        layout.addLayout(input_layout)
        
        # List
        self.task_list = QListWidget()
        self.task_list.itemDoubleClicked.connect(self.toggle_task)
        layout.addWidget(self.task_list)
        
        # Delete Button
        self.del_btn = QPushButton("DELETE SELECTED")
        self.del_btn.clicked.connect(self.delete_task)
        layout.addWidget(self.del_btn)
        
        self.refresh_list()

    def add_task(self):
        text = self.task_input.text().strip()
        if text:
            self.data_manager.add_task(text)
            self.task_input.clear()
            self.refresh_list()

    def delete_task(self):
        item = self.task_list.currentItem()
        if item:
            task_id = item.data(Qt.UserRole)
            self.data_manager.delete_task(task_id)
            self.refresh_list()

    def toggle_task(self, item):
        task_id = item.data(Qt.UserRole)
        self.data_manager.toggle_task(task_id)
        self.refresh_list()

    def refresh_list(self):
        self.task_list.clear()
        tasks = self.data_manager.get_tasks()
        for t in tasks:
            status = "[X]" if t['completed'] else "[ ]"
            display_text = f"{status} {t['title']}"
            item = QListWidgetItem(display_text)
            item.setData(Qt.UserRole, t['id'])
            if t['completed']:
                item.setForeground(Qt.gray)
            self.task_list.addItem(item)
