from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, 
                             QPushButton, QLineEdit, QCheckBox, QFrame, QSlider, QSplitter, QListWidget)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QFont
from src.core.habits_manager import HabitsManager
from src.core.stats_manager import StatsManager
from datetime import datetime

class TaskItem(QWidget):
    changed = pyqtSignal()

    def __init__(self, text="", done=False, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        
        self.checkbox = QCheckBox()
        self.checkbox.blockSignals(True) # Prevent signal during init
        self.checkbox.setChecked(done)
        self.checkbox.blockSignals(False)
        self.checkbox.stateChanged.connect(self.emit_change)
        
        self.input = QLineEdit(text)
        self.input.setFrame(False)
        self.input.setStyleSheet("background: transparent; border: none; border-bottom: 1px solid #333;")
        self.input.editingFinished.connect(self.emit_change)
        
        layout.addWidget(self.checkbox)
        layout.addWidget(self.input)
        
        # Set initial style without emitting signal
        self.update_style()
        
    def emit_change(self):
        self.update_style()
        self.changed.emit()

    def update_style(self):
        if self.checkbox.isChecked():
            self.input.setStyleSheet("background: transparent; border: none; color: #555; text-decoration: line-through;")
        else:
            self.input.setStyleSheet("background: transparent; border: none; border-bottom: 1px solid #333; color: #00FF00;")

    def get_data(self):
        return {"text": self.input.text(), "done": self.checkbox.isChecked()}

class SectionWidget(QFrame):
    data_changed = pyqtSignal()

    def __init__(self, title, color_class, parent=None):
        super().__init__(parent)
        self.setProperty("class", f"Card {color_class}")
        self.layout = QVBoxLayout(self)
        
        header_layout = QHBoxLayout()
        self.label = QLabel(title)
        self.label.setStyleSheet("font-weight: bold; font-size: 18px;")
        header_layout.addWidget(self.label)
        
        self.add_btn = QPushButton("+")
        self.add_btn.setFixedSize(30, 30)
        self.add_btn.clicked.connect(lambda: self.add_item("", False, True)) # User added
        header_layout.addWidget(self.add_btn)
        
        self.layout.addLayout(header_layout)
        self.items_layout = QVBoxLayout()
        self.layout.addLayout(self.items_layout)

    def add_item(self, text="", done=False, user_action=False):
        item = TaskItem(text, done)
        item.changed.connect(self.data_changed.emit)
        self.items_layout.addWidget(item)
        if user_action:
            self.data_changed.emit() # Save immediately on new item
        return item

    def get_items(self):
        items = []
        for i in range(self.items_layout.count()):
            widget = self.items_layout.itemAt(i).widget()
            if widget and widget.input.text().strip():
                items.append(widget.get_data())
        return items

    def clear_items(self):
        while self.items_layout.count():
            item = self.items_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

class TaskPage(QWidget):
    def __init__(self):
        super().__init__()
        self.manager = HabitsManager()
        self.stats = StatsManager()
        self.current_date = datetime.now().strftime("%Y-%m-%d")
        
        main_layout = QHBoxLayout(self)
        
        # Left: History & Stats
        left_panel = QFrame()
        left_panel.setFixedWidth(250)
        left_panel.setStyleSheet("background-color: #050505; border-right: 1px solid #003300;")
        left_layout = QVBoxLayout(left_panel)
        
        left_layout.addWidget(QLabel("HISTORY"))
        self.history_list = QListWidget()
        self.history_list.itemClicked.connect(self.load_history_date)
        left_layout.addWidget(self.history_list)
        
        left_layout.addWidget(QLabel("STATS"))
        self.stats_lbl = QLabel()
        self.stats_lbl.setWordWrap(True)
        left_layout.addWidget(self.stats_lbl)
        
        # Right: Daily Log
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Header
        self.date_header = QLabel(f"LOG: {self.current_date}")
        self.date_header.setObjectName("Header")
        right_layout.addWidget(self.date_header)
        
        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        
        # Sections
        self.protocols = SectionWidget("PROTOCOLS (B Tasks)", "SectionProtocols")
        self.main_tasks = SectionWidget("MAIN OBJECTIVES (A Tasks)", "SectionMain")
        self.outreach = SectionWidget("OUTREACH", "SectionOutreach")
        self.gratitude = SectionWidget("GRATITUDE", "")
        
        self.protocols.data_changed.connect(self.save_current_day)
        self.main_tasks.data_changed.connect(self.save_current_day)
        self.outreach.data_changed.connect(self.save_current_day)
        self.gratitude.data_changed.connect(self.save_current_day)
        
        self.content_layout.addWidget(self.protocols)
        self.content_layout.addWidget(self.main_tasks)
        self.content_layout.addWidget(self.outreach)
        self.content_layout.addWidget(self.gratitude)
        
        # Lesson
        self.content_layout.addWidget(QLabel("LESSON / REFLECTION"))
        self.lesson_input = QLineEdit()
        self.lesson_input.editingFinished.connect(self.save_current_day)
        self.content_layout.addWidget(self.lesson_input)
        
        # Ratings
        ratings_layout = QHBoxLayout()
        
        self.mood_slider = self.create_slider("MOOD")
        self.prod_slider = self.create_slider("PRODUCTIVITY")
        
        ratings_layout.addWidget(self.mood_slider['widget'])
        ratings_layout.addWidget(self.prod_slider['widget'])
        self.content_layout.addLayout(ratings_layout)
        
        scroll.setWidget(content)
        right_layout.addWidget(scroll)
        
        main_layout.addWidget(left_panel)
        main_layout.addWidget(right_panel)
        
        self.refresh_history()
        self.load_day(self.current_date)

    def create_slider(self, label):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        lbl = QLabel(f"{label}: 5/10")
        slider = QSlider(Qt.Horizontal)
        slider.setRange(1, 10)
        slider.setValue(5)
        slider.valueChanged.connect(lambda v: lbl.setText(f"{label}: {v}/10"))
        slider.valueChanged.connect(self.save_current_day)
        layout.addWidget(lbl)
        layout.addWidget(slider)
        return {"widget": widget, "slider": slider, "label": lbl, "name": label}

    def load_day(self, date_str):
        self.current_date = date_str
        self.date_header.setText(f"LOG: {date_str}")
        data = self.manager.get_day(date_str)
        
        self.protocols.clear_items()
        for item in data.get('protocols', []):
            self.protocols.add_item(item['text'], item['done'])
            
        self.main_tasks.clear_items()
        for item in data.get('main', []):
            self.main_tasks.add_item(item['text'], item['done'])
            
        self.outreach.clear_items()
        for item in data.get('outreach', []):
            self.outreach.add_item(item['text'], item['done'])
            
        self.gratitude.clear_items()
        for item in data.get('gratitude', []):
            text = item['text'] if isinstance(item, dict) else item
            self.gratitude.add_item(text, True)
            
        self.lesson_input.setText(data.get('lesson', ''))
        
        self.mood_slider['slider'].setValue(data.get('mood', 5))
        self.prod_slider['slider'].setValue(data.get('productivity', 5))
        
        self.update_stats_display()

    def save_current_day(self):
        data = {
            "protocols": self.protocols.get_items(),
            "main": self.main_tasks.get_items(),
            "outreach": self.outreach.get_items(),
            "gratitude": self.gratitude.get_items(),
            "lesson": self.lesson_input.text(),
            "mood": self.mood_slider['slider'].value(),
            "productivity": self.prod_slider['slider'].value()
        }
        self.manager.update_day(self.current_date, data)
        self.update_stats_display()

    def refresh_history(self):
        self.history_list.clear()
        dates = sorted(self.manager.data.keys(), reverse=True)
        for d in dates:
            self.history_list.addItem(d)

    def load_history_date(self, item):
        self.load_day(item.text())

    def update_stats_display(self):
        streak = self.stats.get_streak()
        completion = self.stats.get_daily_completion(self.current_date)
        
        text = f"""
        STREAK: {streak} DAYS
        TODAY: {completion:.1f}%
        """
        self.stats_lbl.setText(text)
