from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTreeWidget, QTreeWidgetItem, QHBoxLayout, QLineEdit, QPushButton
from src.core.data_manager import DataManager

class FuturePlansPage(QWidget):
    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()
        layout = QVBoxLayout(self)
        
        header = QLabel("LONG_TERM_STRATEGY")
        header.setObjectName("Header")
        layout.addWidget(header)
        
        # Input
        input_layout = QHBoxLayout()
        self.goal_input = QLineEdit()
        self.goal_input.setPlaceholderText("New Goal...")
        self.cat_input = QLineEdit()
        self.cat_input.setPlaceholderText("Category (e.g., CAREER, SKILLS)")
        self.add_btn = QPushButton("COMMIT")
        self.add_btn.clicked.connect(self.add_plan)
        
        input_layout.addWidget(self.goal_input)
        input_layout.addWidget(self.cat_input)
        input_layout.addWidget(self.add_btn)
        layout.addLayout(input_layout)
        
        # Tree View
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Goal", "Category", "Status"])
        self.tree.setColumnWidth(0, 300)
        layout.addWidget(self.tree)
        
        self.refresh_list()

    def add_plan(self):
        goal = self.goal_input.text().strip()
        cat = self.cat_input.text().strip()
        if goal:
            self.data_manager.add_plan(goal, cat)
            self.goal_input.clear()
            self.cat_input.clear()
            self.refresh_list()

    def refresh_list(self):
        self.tree.clear()
        plans = self.data_manager.get_plans()
        for p in plans:
            item = QTreeWidgetItem([p['goal'], p['category'], "PENDING"])
            self.tree.addTopLevelItem(item)
