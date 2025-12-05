from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QScrollArea, 
                             QPushButton, QLineEdit, QCheckBox, QFrame, QSplitter, QListWidget, QMenu, QAction, QDialog, QCalendarWidget, QDialogButtonBox)
from PyQt5.QtCore import Qt, QDate, pyqtSignal
from PyQt5.QtGui import QIntValidator
from src.core.habits_manager import HabitsManager
from src.core.stats_manager import StatsManager
from datetime import datetime

class ClickableLabel(QLabel):
    clicked = pyqtSignal()
    double_clicked = pyqtSignal()

    def mouseReleaseEvent(self, event):
        self.clicked.emit()
        super().mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        self.double_clicked.emit()
        super().mouseDoubleClickEvent(event)

class TaskItem(QWidget):
    changed = pyqtSignal()
    delete_requested = pyqtSignal()

    def __init__(self, text="", done=False, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        
        self.done = done
        
        # Status Label [ ] or [x]
        self.status_lbl = ClickableLabel()
        self.status_lbl.setStyleSheet("font-family: 'Consolas'; font-weight: bold; color: #00FF00; margin-right: 5px;")
        self.status_lbl.setCursor(Qt.PointingHandCursor)
        # Toggle on click or double click (User asked for double click, but click is better UX for brackets. 
        # I'll support both or just click on bracket, double click on widget?)
        # Let's make the bracket toggle on click for ease, but user said "double click it". 
        # I'll bind double click on the whole widget to toggle too.
        self.status_lbl.clicked.connect(self.toggle_status)
        
        self.input = QLineEdit(text)
        self.input.setFrame(False)
        self.input.setStyleSheet("background: transparent; border: none; border-bottom: 1px solid #333; color: #00FF00;")
        self.input.editingFinished.connect(self.emit_change)
        
        # Delete button (small 'x')
        self.del_btn = QPushButton("x")
        self.del_btn.setFixedSize(20, 20)
        self.del_btn.setStyleSheet("border: none; color: #888; font-weight: bold;")
        self.del_btn.clicked.connect(self.delete_requested.emit)
        
        layout.addWidget(self.status_lbl)
        layout.addWidget(self.input)
        layout.addWidget(self.del_btn)
        
        self.update_style()

    def mouseDoubleClickEvent(self, event):
        # Allow toggling by double clicking anywhere on the row (except input might consume it)
        self.toggle_status()
        super().mouseDoubleClickEvent(event)
        
    def toggle_status(self):
        self.done = not self.done
        self.emit_change()

    def emit_change(self):
        self.update_style()
        self.changed.emit()

    def update_style(self):
        if self.done:
            self.status_lbl.setText("[x]")
            self.status_lbl.setStyleSheet("font-family: 'Consolas'; font-weight: bold; color: #00FFFF;") # Cyan for done
            # Visible gray for done tasks, not black/dark gray
            self.input.setStyleSheet("background: transparent; border: none; color: #AAAAAA; text-decoration: line-through;")
        else:
            self.status_lbl.setText("[ ]")
            self.status_lbl.setStyleSheet("font-family: 'Consolas'; font-weight: bold; color: #00FF00;") # Green for open
            self.input.setStyleSheet("background: transparent; border: none; border-bottom: 1px solid #333; color: #00FF00;")

    def set_read_only(self, readonly):
        self.input.setReadOnly(readonly)
        self.del_btn.setVisible(not readonly)
        # Disable interaction with status label
        self.status_lbl.setEnabled(not readonly)
        
        if readonly:
            self.input.setStyleSheet("background: transparent; border: none; color: #666;")
            self.status_lbl.setStyleSheet("font-family: 'Consolas'; font-weight: bold; color: #666; margin-right: 5px;")
        else:
            self.update_style()

    def get_data(self):
        return {"text": self.input.text(), "done": self.done}

class CollapsibleSection(QFrame):
    data_changed = pyqtSignal()

    def __init__(self, title, color_hex, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Header Button
        self.toggle_btn = QPushButton(f"▼ {title}")
        self.toggle_btn.setStyleSheet(f"text-align: left; font-weight: bold; font-size: 16px; color: {color_hex}; border: 1px solid {color_hex}; padding: 5px; background-color: #111;")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.setChecked(True)
        self.toggle_btn.clicked.connect(self.toggle_content)
        self.layout.addWidget(self.toggle_btn)
        
        # Content Area
        self.content_area = QWidget()
        self.content_layout = QVBoxLayout(self.content_area)
        self.layout.addWidget(self.content_area)
        
        # Add Item Button inside content
        self.add_btn = QPushButton("+ ADD ITEM")
        self.add_btn.setStyleSheet(f"color: {color_hex}; border: 1px dashed {color_hex}; margin-top: 5px;")
        self.add_btn.clicked.connect(lambda: self.add_item("", False, True))
        self.content_layout.addWidget(self.add_btn)
        
        self.items_layout = QVBoxLayout()
        self.content_layout.addLayout(self.items_layout)

    def set_read_only(self, readonly):
        self.add_btn.setVisible(not readonly)
        for i in range(self.items_layout.count()):
            widget = self.items_layout.itemAt(i).widget()
            if widget:
                widget.set_read_only(readonly)

    def toggle_content(self):
        if self.toggle_btn.isChecked():
            self.content_area.show()
            self.toggle_btn.setText(self.toggle_btn.text().replace("▶", "▼"))
        else:
            self.content_area.hide()
            self.toggle_btn.setText(self.toggle_btn.text().replace("▼", "▶"))

    def add_item(self, text="", done=False, user_action=False):
        item = TaskItem(text, done)
        item.changed.connect(self.data_changed.emit)
        item.delete_requested.connect(lambda: self.remove_item(item))
        self.items_layout.addWidget(item)
        if user_action:
            self.data_changed.emit()
        return item

    def remove_item(self, item):
        self.items_layout.removeWidget(item)
        item.deleteLater()
        self.data_changed.emit()

    def get_items(self):
        items = []
        for i in range(self.items_layout.count()):
            widget = self.items_layout.itemAt(i).widget()
            if widget:
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
        
        # Splitter for Responsive Layout
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # Left: History & Stats
        left_panel = QFrame()
        left_panel.setMinimumWidth(200) # Allow resizing but keep min width
        left_panel.setStyleSheet("background-color: #050505; border-right: 1px solid #003300;")
        left_layout = QVBoxLayout(left_panel)
        
        left_layout.addWidget(QLabel("HISTORY LOG"))
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
        header_layout = QHBoxLayout()
        self.date_header = QLabel(f"LOG: {self.current_date}")
        self.date_header.setObjectName("Header")
        header_layout.addWidget(self.date_header)
        
        # Plan Future Button (Responsive)
        self.plan_btn = QPushButton("PLAN FUTURE")
        self.plan_btn.clicked.connect(self.open_calendar)
        # Removed fixed width
        header_layout.addWidget(self.plan_btn)

        self.save_btn = QPushButton("SAVE (Ctrl+S)")
        self.save_btn.setShortcut("Ctrl+S")
        self.save_btn.clicked.connect(self.save_current_day)
        self.save_btn.setFixedWidth(150)
        header_layout.addWidget(self.save_btn)
        
        right_layout.addLayout(header_layout)
        
        # Scroll Area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        content = QWidget()
        self.content_layout = QVBoxLayout(content)
        
        # Sections with different colors
        self.protocols = CollapsibleSection("PROTOCOLS (B Tasks)", "#00FF00") # Green
        self.main_tasks = CollapsibleSection("MAIN OBJECTIVES (A Tasks)", "#00FFFF") # Cyan
        self.outreach = CollapsibleSection("OUTREACH", "#FF0033") # Red
        self.gratitude = CollapsibleSection("GRATITUDE", "#FFFF00") # Yellow
        
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
        
        # Ratings (Inputs instead of sliders)
        ratings_layout = QHBoxLayout()
        
        self.mood_input = self.create_rating_input("MOOD (1-10)")
        self.prod_input = self.create_rating_input("PRODUCTIVITY (1-10)")
        
        ratings_layout.addWidget(self.mood_input['widget'])
        ratings_layout.addWidget(self.prod_input['widget'])
        self.content_layout.addLayout(ratings_layout)
        
        scroll.setWidget(content)
        right_layout.addWidget(scroll)
        
        # Add panels to splitter
        splitter.addWidget(left_panel)
        splitter.addWidget(right_panel)
        splitter.setSizes([250, 800])
        
        self.refresh_history()
        self.load_day(self.current_date)

    def create_rating_input(self, label):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        lbl = QLabel(label)
        inp = QLineEdit()
        inp.setValidator(QIntValidator(1, 10))
        inp.editingFinished.connect(self.save_current_day)
        layout.addWidget(lbl)
        layout.addWidget(inp)
        return {"widget": widget, "input": inp}

    def open_calendar(self):
        dlg = QDialog(self)
        dlg.setWindowTitle("Select Date to Plan")
        dlg.setStyleSheet("background-color: #111; color: #00FF00;")
        layout = QVBoxLayout(dlg)
        
        cal = QCalendarWidget()
        cal.setStyleSheet("background-color: #222; color: #000;")
        cal.setGridVisible(True)
        layout.addWidget(cal)
        
        btns = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        btns.accepted.connect(dlg.accept)
        btns.rejected.connect(dlg.reject)
        layout.addWidget(btns)
        
        if dlg.exec_():
            date = cal.selectedDate().toString("yyyy-MM-dd")
            self.load_day(date)

    def load_day(self, date_str):
        self.current_date = date_str
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        # Determine if read-only (Past dates are read-only)
        is_past = date_str < today_str
        
        # Format header with day name
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        day_name = dt.strftime('%A')
        
        header_text = f"LOG: {date_str} ({day_name})"
        if date_str == today_str:
            header_text += " [TODAY]"
        elif is_past:
            header_text += " [READ-ONLY]"
        else:
            header_text += " [FUTURE PLAN]"
            
        self.date_header.setText(header_text)
        
        # Load data
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
        
        self.mood_input['input'].setText(str(data.get('mood', 5)))
        self.prod_input['input'].setText(str(data.get('productivity', 5)))
        
        self.update_stats_display()
        self.set_read_only(is_past)

    def set_read_only(self, readonly):
        self.protocols.set_read_only(readonly)
        self.main_tasks.set_read_only(readonly)
        self.outreach.set_read_only(readonly)
        self.gratitude.set_read_only(readonly)
        
        self.lesson_input.setReadOnly(readonly)
        self.mood_input['input'].setReadOnly(readonly)
        self.prod_input['input'].setReadOnly(readonly)
        self.save_btn.setVisible(not readonly)

from src.core.router import Router

    def save_current_day(self):
        # Don't save if read-only (double check, though UI should prevent it)
        today_str = datetime.now().strftime("%Y-%m-%d")
        if self.current_date < today_str:
            return

        try:
            mood_val = int(self.mood_input['input'].text() or 0)
            prod_val = int(self.prod_input['input'].text() or 0)
        except:
            mood_val = 5
            prod_val = 5

        data = {
            "protocols": self.protocols.get_items(),
            "main": self.main_tasks.get_items(),
            "outreach": self.outreach.get_items(),
            "gratitude": self.gratitude.get_items(),
            "lesson": self.lesson_input.text(),
            "mood": mood_val,
            "productivity": prod_val
        }
        self.manager.update_day(self.current_date, data)
        self.update_stats_display()
        self.refresh_history() # Refresh in case it's a new day
        
        # Emit Global Data Changed Signal
        Router.instance().data_changed.emit()

    def refresh_history(self):
        self.history_list.clear()
        # Ensure we are reading from the manager's data which should be loaded
        if not self.manager.data:
            self.manager.load_data()
            
        dates = sorted(self.manager.data.keys(), reverse=True)
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        # Ensure Today is at top if it exists, or just rely on reverse sort (future > today > past)
        # User asked: "show the today in the top". 
        # If there are future dates, they will be above today in reverse sort.
        # If user strictly wants Today FIRST, then future, then past? Or Future -> Today -> Past?
        # Usually "Today" at top implies it's the most relevant. 
        # But if I have a plan for 2025-12-10 and today is 2025-12-02, 
        # seeing 2025-12-10 first is correct for reverse chronological.
        # I will assume reverse chronological is acceptable as long as Today is clearly visible.
        
        for d in dates:
            try:
                dt = datetime.strptime(d, "%Y-%m-%d")
                # 3 char day: %a
                display = f"{d} ({dt.strftime('%a')})"
                if d == today_str:
                    display = f"[TODAY] {display}" 
                    # Highlight today
            except:
                display = d
            self.history_list.addItem(display)
            
    def load_history_date(self, item):
        # Extract date string "YYYY-MM-DD"
        # Item text might be "[TODAY] 2025-12-02 (Tue)" or "2025-12-01 (Mon)"
        text = item.text()
        if "[TODAY]" in text:
            text = text.replace("[TODAY] ", "")
        
        date_str = text.split(' ')[0]
        self.load_day(date_str)

    def update_stats_display(self):
        streak = self.stats.get_streak()
        completion = self.stats.get_daily_completion(self.current_date)
        
        text = f"""
        STREAK: {streak} DAYS
        COMPLETION: {completion:.1f}%
        """
        self.stats_lbl.setText(text)
