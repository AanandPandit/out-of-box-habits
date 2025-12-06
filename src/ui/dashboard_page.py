from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, 
                             QFrame, QScrollArea, QPushButton, QProgressBar, QSizePolicy, QInputDialog, QComboBox, QDialog, QLineEdit, QCalendarWidget, QDialogButtonBox, QSplitter)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal, QDate
from PyQt5.QtGui import QColor, QFont
from datetime import datetime
import psutil
import sys
import requests
import socket

# Matplotlib integration
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from src.core.data_manager import DataManager
from src.core.habits_manager import HabitsManager
from src.core.stats_manager import StatsManager
from src.core.router import Router
from src.core.cpp_bridge import CppBridge

# --- Custom Widgets ---

class Panel(QWidget):
    def __init__(self, title, color_hex="#00FF00", parent=None, header_widget=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Header Frame (Consistent with CollapsiblePanel but not clickable)
        self.header_frame = QFrame()
        self.header_frame.setObjectName("HeaderFrame")
        self.header_frame.setStyleSheet(f"""
            #HeaderFrame {{
                background-color: #111;
                border: 1px solid {color_hex};
                border-bottom: 2px solid {color_hex}; 
            }}
        """)
        
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(5, 5, 5, 5)
        
        self.title_lbl = QLabel(title)
        self.title_lbl.setStyleSheet(f"color: {color_hex}; font-weight: bold; font-size: 16px; border: none; background: transparent;")
        header_layout.addWidget(self.title_lbl)
        
        header_layout.addStretch()
        
        if header_widget:
            header_layout.addWidget(header_widget)
            
        self.layout.addWidget(self.header_frame)
        
        # Content Area
        self.content_area = QWidget()
        self.content_area.setStyleSheet(f"border: 1px solid {color_hex}; border-top: none;")
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(5, 5, 5, 5)
        self.layout.addWidget(self.content_area)

class CollapsiblePanel(QWidget):
    def __init__(self, title, color_hex="#00FF00", parent=None, header_widget=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)
        
        # Header Frame (mimics QPushButton style from task_page.py)
        self.header_frame = QFrame()
        self.header_frame.setObjectName("HeaderFrame")
        self.header_frame.setStyleSheet(f"""
            #HeaderFrame {{
                background-color: #111;
                border: 1px solid {color_hex};
            }}
        """)
        self.header_frame.setCursor(Qt.PointingHandCursor)
        self.header_frame.mouseReleaseEvent = self.toggle_content
        
        header_layout = QHBoxLayout(self.header_frame)
        header_layout.setContentsMargins(5, 5, 5, 5)
        
        self.toggle_lbl = QLabel(f"▼ {title}")
        self.toggle_lbl.setStyleSheet(f"color: {color_hex}; font-weight: bold; font-size: 16px; border: none; background: transparent;")
        header_layout.addWidget(self.toggle_lbl)
        
        header_layout.addStretch()
        
        if header_widget:
            header_layout.addWidget(header_widget)
            
        self.layout.addWidget(self.header_frame)
        
        # Content Area
        self.content_area = QWidget()
        self.content_area.setStyleSheet(f"border: 1px solid {color_hex}; border-top: none;")
        self.content_layout = QVBoxLayout(self.content_area)
        self.content_layout.setContentsMargins(5, 5, 5, 5)
        self.layout.addWidget(self.content_area)
        
    def toggle_content(self, event=None):
        if self.content_area.isVisible():
            self.content_area.hide()
            self.toggle_lbl.setText(self.toggle_lbl.text().replace("▼", "▶"))
            self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)
        else:
            self.content_area.show()
            self.toggle_lbl.setText(self.toggle_lbl.text().replace("▶", "▼"))
            self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.updateGeometry()

class StatValue(QWidget):
    def __init__(self, label, value, color="#00FFFF"):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        
        self.val_lbl = QLabel(str(value))
        self.val_lbl.setStyleSheet(f"color: {color}; font-size: 20px; font-weight: bold; border: none;")
        self.val_lbl.setAlignment(Qt.AlignCenter)
        
        self.lbl = QLabel(label)
        self.lbl.setStyleSheet("color: #888; font-size: 10px; border: none;")
        self.lbl.setAlignment(Qt.AlignCenter)
        
        layout.addWidget(self.val_lbl)
        layout.addWidget(self.lbl)

    def set_value(self, value):
        self.val_lbl.setText(str(value))

class SystemMonitor(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        
        self.cpu_bar = self.create_bar("CPU")
        self.ram_bar = self.create_bar("RAM")
        self.uptime_lbl = QLabel("UPTIME: 00:00:00")
        self.uptime_lbl.setStyleSheet("color: #00FF00; font-family: 'Consolas'; font-size: 10px; border: none;")
        
        layout.addWidget(self.uptime_lbl)
        
        self.start_time = datetime.now()

    def create_bar(self, label):
        container = QWidget()
        l = QHBoxLayout(container)
        l.setContentsMargins(0,0,0,0)
        lbl = QLabel(label)
        lbl.setStyleSheet("color: #00FF00; font-size: 10px; border: none; width: 30px;")
        bar = QProgressBar()
        bar.setStyleSheet("""
            QProgressBar { border: 1px solid #333; background: #111; height: 8px; border-radius: 2px; }
            QProgressBar::chunk { background-color: #00FF00; }
        """)
        bar.setTextVisible(False)
        l.addWidget(lbl)
        l.addWidget(bar)
        self.layout().addWidget(container)
        return bar

    def update_stats(self):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        self.cpu_bar.setValue(int(cpu))
        self.ram_bar.setValue(int(ram))
        
        delta = datetime.now() - self.start_time
        self.uptime_lbl.setText(f"UPTIME: {str(delta).split('.')[0]}")

class ChartsPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        
        self.figure = Figure(facecolor='#050505')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: #050505; border: none;")
        layout.addWidget(self.canvas)
        
    def plot_data(self, trend_data):
        self.figure.clear()
        
        # Dark theme for plots
        plt.style.use('dark_background')
        
        # Single Graph: Multi-metric Trend
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('#050505')
        
        # Data
        x = range(len(trend_data))
        y_prod = [d['productivity'] for d in trend_data]
        y_mood = [d['mood'] for d in trend_data]
        y_comp = [d['completed'] for d in trend_data]
        y_missed = [d['missed'] for d in trend_data]
        
        # Plot Lines
        ax.plot(x, y_prod, color='#00FFFF', marker='o', markersize=4, label='Productivity', linewidth=2)
        ax.plot(x, y_mood, color='#FF00FF', marker='x', markersize=4, label='Mood', linewidth=1, linestyle='--')
        ax.plot(x, y_comp, color='#00FF00', marker='s', markersize=4, label='Completed', linewidth=1.5)
        ax.plot(x, y_missed, color='#FF0000', marker='v', markersize=4, label='Missed', linewidth=1.5)
        
        ax.set_title('PERFORMANCE METRICS', fontsize=10, color='#00FF00')
        ax.tick_params(labelsize=8, colors='#888')
        ax.legend(fontsize=8, facecolor='#111', edgecolor='#333', loc='upper left')
        ax.grid(True, color='#111', linestyle='--')
        
        # Set x-axis labels to dates if few enough points
        if len(trend_data) <= 14:
            dates = [d['date'][5:] for d in trend_data] # MM-DD
            ax.set_xticks(x)
            ax.set_xticklabels(dates, rotation=45)
        
        self.figure.tight_layout()
        self.canvas.draw()

class TerminalDialog(QDialog):
    def __init__(self, parent=None, title="ADD_LONG_TERM_GOAL", default_text="", default_date=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Dialog)
        self.setStyleSheet("""
            QDialog {
                background-color: #050505;
                border: 2px solid #00FF00;
            }
            QLabel {
                color: #00FF00;
                font-family: 'Consolas';
                font-size: 14px;
            }
            QLineEdit {
                background-color: #111;
                color: #00FF00;
                border: 1px solid #003300;
                padding: 5px;
                font-family: 'Consolas';
            }
            QPushButton {
                background-color: #111;
                color: #00FF00;
                border: 1px solid #003300;
                padding: 5px 15px;
                font-family: 'Consolas';
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #003300;
                color: #00FFFF;
            }
            QCalendarWidget QWidget {
                background-color: #050505;
                color: #00FF00;
            }
            QCalendarWidget QAbstractItemView:enabled {
                color: #00FF00;
                background-color: #050505;
                selection-background-color: #003300;
                selection-color: #00FFFF;
            }
        """)
        self.setFixedSize(400, 450)
        
        layout = QVBoxLayout(self)
        
        # Title
        self.title_lbl = QLabel(f">> {title}")
        self.title_lbl.setStyleSheet("font-weight: bold; font-size: 16px; margin-bottom: 10px;")
        layout.addWidget(self.title_lbl)
        
        # Goal Input
        layout.addWidget(QLabel("GOAL_OBJECTIVE:"))
        self.goal_input = QLineEdit(default_text)
        self.goal_input.setPlaceholderText("Enter your goal...")
        layout.addWidget(self.goal_input)
        
        # Date Input (Calendar)
        layout.addWidget(QLabel("TARGET_DATE:"))
        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)
        if default_date:
            try:
                qdate = QDate.fromString(default_date, "yyyy-MM-dd")
                self.calendar.setSelectedDate(qdate)
            except:
                self.calendar.setSelectedDate(QDate.currentDate())
        else:
            self.calendar.setSelectedDate(QDate.currentDate())
            
        layout.addWidget(self.calendar)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        cancel_btn = QPushButton("CANCEL")
        cancel_btn.clicked.connect(self.reject)
        
        ok_btn = QPushButton("CONFIRM")
        ok_btn.clicked.connect(self.accept)
        
        btn_layout.addStretch()
        btn_layout.addWidget(cancel_btn)
        btn_layout.addWidget(ok_btn)
        layout.addLayout(btn_layout)

    def get_data(self):
        date = self.calendar.selectedDate().toString("yyyy-MM-dd")
        return self.goal_input.text(), date

class GoalItem(QWidget):
    toggled = pyqtSignal(int) # Emits project ID
    edit_requested = pyqtSignal(int) # Emits project ID

    def __init__(self, project, parent=None):
        super().__init__(parent)
        self.project = project
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 2, 0, 2)
        
        # Checkbox style label
        status_text = "[*]" if project.get('completed') else "[ ]"
        color = "#00FFFF" if project.get('completed') else "#00FF00"
        
        self.status_lbl = QLabel(status_text)
        self.status_lbl.setStyleSheet(f"font-family: 'Consolas'; font-weight: bold; color: {color}; margin-right: 5px;")
        self.status_lbl.setCursor(Qt.PointingHandCursor)
        # Use mousePressEvent for better responsiveness
        self.status_lbl.mousePressEvent = self.on_toggle
        
        # Goal Text
        self.text_lbl = QLabel(project['name'])
        style = "color: #AAAAAA; text-decoration: line-through;" if project.get('completed') else "color: #00FF00;"
        self.text_lbl.setStyleSheet(f"font-family: 'Consolas'; font-size: 12px; border: none; {style}")
        self.text_lbl.setCursor(Qt.PointingHandCursor)
        self.text_lbl.mouseDoubleClickEvent = self.on_edit # Double click to edit
        
        layout.addWidget(self.status_lbl)
        layout.addWidget(self.text_lbl)
        layout.addStretch()
        
        # Deadline / Days Left
        deadline = project.get('deadline')
        if deadline and not project.get('completed'):
            try:
                target = datetime.strptime(deadline, "%Y-%m-%d")
                delta = (target - datetime.now()).days
                if delta < 0:
                    time_str = f"OVERDUE ({abs(delta)}d)"
                    color = "#FF0000"
                else:
                    time_str = f"{delta}d LEFT"
                    color = "#FFFF00"
                
                time_lbl = QLabel(time_str)
                time_lbl.setStyleSheet(f"color: {color}; font-size: 10px; font-weight: bold;")
                layout.addWidget(time_lbl)
            except:
                pass
        
        # Edit Button (Small pencil or similar, using text for now)
        edit_btn = QPushButton("✎")
        edit_btn.setFixedSize(20, 20)
        edit_btn.setStyleSheet("background: transparent; color: #888; border: none;")
        edit_btn.setCursor(Qt.PointingHandCursor)
        edit_btn.clicked.connect(self.on_edit)
        layout.addWidget(edit_btn)

    def on_toggle(self, event):
        self.toggled.emit(self.project['id'])
        
    def on_edit(self, event=None):
        self.edit_requested.emit(self.project['id'])

# --- Main Dashboard Page ---

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()
        self.habits_manager = HabitsManager()
        self.stats_manager = StatsManager()
        
        self.stats_manager = StatsManager()
        
        # Main Layout with Splitter (Responsive like task_page.py)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)
        
        # --- Left Column (Performance & Analytics) ---
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(10)
        
        # 1. Daily Task Performance Panel
        self.perf_panel = Panel("DAILY PERFORMANCE", "#00FF00")
        perf_layout = QGridLayout()
        self.perf_panel.content_layout.addLayout(perf_layout)
        
        self.stat_total = StatValue("TOTAL", 0)
        self.stat_done = StatValue("DONE", 0, "#00FF00")
        self.stat_missed = StatValue("MISSED", 0, "#FF0000")
        self.stat_pending = StatValue("PENDING", 0, "#FFFF00")
        self.stat_comp_rate = StatValue("COMPLETION", "0%", "#00FFFF")
        self.stat_improv = StatValue("IMPROVEMENT", "0%", "#FF00FF")
        
        perf_layout.addWidget(self.stat_total, 0, 0)
        perf_layout.addWidget(self.stat_done, 0, 1)
        perf_layout.addWidget(self.stat_missed, 0, 2)
        perf_layout.addWidget(self.stat_pending, 1, 0)
        perf_layout.addWidget(self.stat_comp_rate, 1, 1)
        perf_layout.addWidget(self.stat_improv, 1, 2)
        
        self.charts_panel = Panel("ANALYTICS", "#FF00FF", header_widget=self.filter_combo)
        self.charts = ChartsPanel()
        self.charts_panel.content_layout.addWidget(self.charts)
        left_layout.addWidget(self.charts_panel)
        left_layout.addStretch() # Push content up
        
        # --- Right Column (System, Goals, Timeline) ---
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(10)
        
        # 2. System Status Panel
        self.sys_panel = Panel("SYSTEM STATUS", "#00FFFF")
        self.sys_monitor = SystemMonitor()
        self.sys_panel.content_layout.addWidget(self.sys_monitor)
        
        # Add AI Uplink Status
        self.ai_status = QLabel("AI UPLINK: CHECKING...")
        self.ai_status.setStyleSheet("color: #FFFF00; font-size: 10px; border: none; margin-top: 5px;")
        self.sys_panel.content_layout.addWidget(self.ai_status)
        
        right_layout.addWidget(self.sys_panel)
        
        # 4. Long Term Goals Panel
        # Add Goal Button to Header
        add_goal_btn = QPushButton("+")
        add_goal_btn.setFixedSize(20, 20)
        add_goal_btn.setStyleSheet("background: transparent; color: #00FFFF; border: none; font-weight: bold; font-size: 16px;")
        add_goal_btn.setCursor(Qt.PointingHandCursor)
        add_goal_btn.clicked.connect(self.add_goal)
        
        self.obj_panel = CollapsiblePanel("LONG TERM GOALS", "#00FFFF", header_widget=add_goal_btn)
        
        self.obj_layout = QVBoxLayout()
        self.obj_panel.content_layout.addLayout(self.obj_layout)
        right_layout.addWidget(self.obj_panel)
        
        # 5. Today Timeline
        self.timeline_panel = CollapsiblePanel("TODAY'S TIMELINE", "#FFFF00")
        self.timeline_scroll = QScrollArea()
        self.timeline_scroll.setWidgetResizable(True)
        self.timeline_scroll.setStyleSheet("border: none; background: transparent;")
        self.timeline_container = QWidget()
        self.timeline_layout = QVBoxLayout(self.timeline_container)
        self.timeline_scroll.setWidget(self.timeline_container)
        self.timeline_panel.content_layout.addWidget(self.timeline_scroll)
        right_layout.addWidget(self.timeline_panel)
        
        right_layout.addStretch() # Push content up
        
        # Add to Splitter
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([400, 600]) # Initial ratio
        
        # Timers
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(2000) # Refresh every 2s
        
        self.sys_timer = QTimer(self)
        self.sys_timer.timeout.connect(self.update_system_stats)
        self.sys_timer.start(1000)
        
        # Internet Check Timer (every 10s)
        self.net_timer = QTimer(self)
        self.net_timer.timeout.connect(self.check_internet)
        self.net_timer.start(10000)
        QTimer.singleShot(100, self.check_internet) # Initial check

        self.current_days_filter = 7
        
        # Initial Load
        self.refresh_data()
        
        # Listen for updates
        Router.instance().data_changed.connect(self.refresh_data)

    def update_system_stats(self):
        self.sys_monitor.update_stats()

    def check_internet(self):
        try:
            # Fast check
            requests.get("http://www.google.com", timeout=2)
            self.ai_status.setText("AI UPLINK: ONLINE")
            self.ai_status.setStyleSheet("color: #00FF00; font-size: 10px; border: none; margin-top: 5px;")
        except:
            self.ai_status.setText("AI UPLINK: OFFLINE")
            self.ai_status.setStyleSheet("color: #FF0000; font-size: 10px; border: none; margin-top: 5px;")

    def on_filter_change(self, index):
        days = 7
        if index == 1: days = 30
        elif index == 2: days = 365
        self.current_days_filter = days
        self.refresh_data()

    def add_goal(self):
        dialog = TerminalDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            goal, date = dialog.get_data()
            if goal:
                # Validate date
                try:
                    if date:
                        datetime.strptime(date, "%Y-%m-%d")
                except ValueError:
                    date = None # Invalid date, ignore
                
                self.data_manager.add_project(goal, "Life Goal", deadline=date)
                # Emit global signal instead of just local refresh
                Router.instance().data_changed.emit()

    def edit_goal(self, project_id):
        # Find project
        projects = self.data_manager.get_projects()
        project = next((p for p in projects if p['id'] == project_id), None)
        if not project: return
        
        dialog = TerminalDialog(self, title="EDIT_GOAL", default_text=project['name'], default_date=project.get('deadline'))
        if dialog.exec_() == QDialog.Accepted:
            name, date = dialog.get_data()
            if name:
                self.data_manager.edit_project(project_id, name, date)
                Router.instance().data_changed.emit()

    def toggle_goal(self, project_id):
        self.data_manager.toggle_project(project_id)
        # Emit global signal
        Router.instance().data_changed.emit()

    def update_charts(self, days):
        # Deprecated, handled by on_filter_change
        pass

    def refresh_data(self):
        today_str = datetime.now().strftime("%Y-%m-%d")
        day_data = self.habits_manager.get_day(today_str)
        
        # 1. Update Performance Panel
        total = 0
        done = 0
        for section in ['protocols', 'main', 'outreach']:
            tasks = day_data.get(section, [])
            total += len(tasks)
            done += sum(1 for t in tasks if t.get('done', False))
            
        pending = total - done
        missed = 0 # Placeholder for today
        
        self.stat_total.set_value(total)
        self.stat_done.set_value(done)
        self.stat_missed.set_value(missed)
        self.stat_pending.set_value(pending)
        
        comp_rate = (done / total * 100) if total > 0 else 0
        self.stat_comp_rate.set_value(f"{comp_rate:.1f}%")
        
        improv = self.stats_manager.get_improvement_rate()
        prefix = "+" if improv >= 0 else ""
        self.stat_improv.set_value(f"{prefix}{improv:.1f}%")
        self.stat_improv.val_lbl.setStyleSheet(f"color: {'#00FF00' if improv >= 0 else '#FF0000'}; font-size: 20px; font-weight: bold; border: none;")

        # 2. Update Charts
        trend = self.stats_manager.get_productivity_trend(self.current_days_filter)
        self.charts.plot_data(trend)
        
        # 3. Update Objectives (Goals)
        # Clear old
        while self.obj_layout.count() > 1: # Keep header at index 0
            item = self.obj_layout.takeAt(1)
            if item.widget(): item.widget().deleteLater()
            
        projects = self.data_manager.get_projects()
        if not projects:
            self.obj_layout.addWidget(QLabel("NO GOALS SET", styleSheet="color: #666; font-style: italic; border: none;"))
        else:
            for p in projects:
                item = GoalItem(p)
                item.toggled.connect(self.toggle_goal)
                item.edit_requested.connect(self.edit_goal)
                self.obj_layout.addWidget(item)
                
        # 4. Update Timeline
        while self.timeline_layout.count():
            item = self.timeline_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        # Collect tasks
        all_tasks = []
        for section in ['protocols', 'main', 'outreach']:
            for item in day_data.get(section, []):
                all_tasks.append({"text": item['text'], "done": item['done'], "section": section})
        
        if not all_tasks:
            self.timeline_layout.addWidget(QLabel("NO TASKS LOGGED", styleSheet="color: #666; border: none;"))
        else:
            for t in all_tasks:
                if t['done']:
                    status = "✔"
                    color = "#00FF00"
                    text = f"{status} [{t['section'].upper()}] {t['text']}"
                else:
                    status = "⚠"
                    color = "#FF0000" # Red for pending
                    text = f"{status} [{t['section'].upper()}] {t['text']}"
                
                lbl = QLabel(text)
                lbl.setStyleSheet(f"color: {color}; font-size: 12px; border: none; padding: 2px; font-weight: {'bold' if not t['done'] else 'normal'};")
                self.timeline_layout.addWidget(lbl)
        
        self.timeline_layout.addStretch()
