from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, QGridLayout, 
                             QFrame, QScrollArea, QPushButton, QProgressBar, QSizePolicy, QInputDialog, QComboBox)
from PyQt5.QtCore import QTimer, Qt, pyqtSignal
from PyQt5.QtGui import QColor, QFont
from datetime import datetime
import psutil
import sys

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

class Panel(QFrame):
    def __init__(self, title, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QFrame {
                background-color: #050505;
                border: 1px solid #003300;
                border-radius: 5px;
            }
        """)
        self.layout = QVBoxLayout(self)
        
        if title:
            self.title_lbl = QLabel(title)
            self.title_lbl.setStyleSheet("color: #00FF00; font-weight: bold; font-size: 14px; border: none;")
            self.layout.addWidget(self.title_lbl)
            
            line = QFrame()
            line.setFrameShape(QFrame.HLine)
            line.setStyleSheet("color: #003300; border: 1px solid #003300;")
            self.layout.addWidget(line)

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
    filter_changed = pyqtSignal(int) # Emits days count

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0,0,0,0)
        
        # Filter Dropdown
        self.filter_combo = QComboBox()
        self.filter_combo.addItems(["Last 7 Days", "Last 30 Days", "All Time"])
        self.filter_combo.setStyleSheet("""
            QComboBox {
                background-color: #111;
                color: #00FF00;
                border: 1px solid #003300;
                padding: 5px;
                font-family: 'Consolas';
            }
            QComboBox::drop-down { border: none; }
            QComboBox QAbstractItemView {
                background-color: #111;
                color: #00FF00;
                selection-background-color: #003300;
            }
        """)
        self.filter_combo.currentIndexChanged.connect(self.on_filter_change)
        
        # Header layout for filter
        header = QHBoxLayout()
        header.addStretch()
        header.addWidget(self.filter_combo)
        layout.addLayout(header)
        
        self.figure = Figure(facecolor='#050505')
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet("background-color: #050505; border: none;")
        layout.addWidget(self.canvas)
        
    def on_filter_change(self, index):
        days = 7
        if index == 1: days = 30
        elif index == 2: days = 365 # All time approx
        self.filter_changed.emit(days)
        
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

# --- Main Dashboard Page ---

class DashboardPage(QWidget):
    def __init__(self):
        super().__init__()
        self.data_manager = DataManager()
        self.habits_manager = HabitsManager()
        self.stats_manager = StatsManager()
        
        self.layout = QGridLayout(self)
        self.layout.setSpacing(10)
        
        # 1. Daily Task Performance Panel (Top Left)
        self.perf_panel = Panel("DAILY PERFORMANCE")
        perf_layout = QGridLayout()
        self.perf_panel.layout.addLayout(perf_layout)
        
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
        
        self.layout.addWidget(self.perf_panel, 0, 0, 1, 1)
        
        # 2. System Status Panel (Top Right)
        self.sys_panel = Panel("SYSTEM STATUS")
        self.sys_monitor = SystemMonitor()
        self.sys_panel.layout.addWidget(self.sys_monitor)
        
        # Add AI Uplink Status
        self.ai_status = QLabel("AI UPLINK: ONLINE")
        self.ai_status.setStyleSheet("color: #00FFFF; font-size: 10px; border: none; margin-top: 5px;")
        self.sys_panel.layout.addWidget(self.ai_status)
        
        self.layout.addWidget(self.sys_panel, 0, 1, 1, 1)
        
        # 3. Charts Section (Middle Left - Spanning)
        self.charts_panel = Panel("ANALYTICS")
        self.charts = ChartsPanel()
        self.charts_panel.layout.addWidget(self.charts)
        self.layout.addWidget(self.charts_panel, 1, 0, 2, 1)
        
        # 4. Main Objectives Panel (Middle Right)
        self.obj_panel = Panel("MAIN OBJECTIVES")
        
        # Add Goal Button to Header
        add_goal_btn = QPushButton("+")
        add_goal_btn.setFixedSize(20, 20)
        add_goal_btn.setStyleSheet("background: transparent; color: #00FF00; border: none; font-weight: bold; font-size: 16px;")
        add_goal_btn.setCursor(Qt.PointingHandCursor)
        add_goal_btn.clicked.connect(self.add_goal)
        
        # Hacky way to put button in header: add to layout of title label's parent? 
        # Better: Panel class should support header widgets. 
        # For now, let's just add it to the panel layout at the top.
        
        # Actually, let's modify the Panel class slightly or just add a header layout here.
        # Since Panel is simple, I'll just add a "Controls" layout at top of obj_panel content.
        
        header_layout = QHBoxLayout()
        header_layout.addStretch()
        header_layout.addWidget(add_goal_btn)
        # Insert at top (index 0 is title, 1 is line, 2 is content layout)
        # But Panel uses VBox. Let's just add it to the obj_layout at top.
        
        self.obj_layout = QVBoxLayout()
        self.obj_layout.addLayout(header_layout) # Add button row
        self.obj_panel.layout.addLayout(self.obj_layout)
        self.layout.addWidget(self.obj_panel, 1, 1, 1, 1)
        
        # 5. Today Timeline (Bottom Right)
        self.timeline_panel = Panel("TODAY'S TIMELINE")
        self.timeline_scroll = QScrollArea()
        self.timeline_scroll.setWidgetResizable(True)
        self.timeline_scroll.setStyleSheet("border: none; background: transparent;")
        self.timeline_container = QWidget()
        self.timeline_layout = QVBoxLayout(self.timeline_container)
        self.timeline_scroll.setWidget(self.timeline_container)
        self.timeline_panel.layout.addWidget(self.timeline_scroll)
        self.layout.addWidget(self.timeline_panel, 2, 1, 1, 1)
        
        # Removed Quick Access Buttons as requested
        
        # Timers
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.refresh_data)
        self.timer.start(2000) # Refresh every 2s
        
        self.sys_timer = QTimer(self)
        self.sys_timer.timeout.connect(self.sys_monitor.update_stats)
        self.sys_timer.start(1000)
        
        # Initial Load
        self.refresh_data()
        
        # Listen for updates
        Router.instance().data_changed.connect(self.refresh_data)

    def add_goal(self):
        text, ok = QInputDialog.getText(self, "Add Life Goal", "Enter your long-term objective:")
        if ok and text:
            self.data_manager.add_project(text, "Life Goal") # Using add_project as proxy for goals
            self.refresh_data()

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
        # For today, missed is 0 unless we define logic. 
        # But let's use the stats manager for consistency if possible, or just calc here.
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
        weekly = self.stats_manager.get_weekly_breakdown()
        trend = self.stats_manager.get_productivity_trend()
        self.charts.plot_data(weekly, trend)
        
        # 3. Update Objectives (Mocking from DataManager projects for now)
        # Clear old
        while self.obj_layout.count():
            item = self.obj_layout.takeAt(0)
            if item.widget(): item.widget().deleteLater()
            
        projects = self.data_manager.get_projects()
        if not projects:
            self.obj_layout.addWidget(QLabel("NO ACTIVE OBJECTIVES", styleSheet="color: #666; font-style: italic; border: none;"))
        else:
            for p in projects[:3]: # Show top 3
                lbl = QLabel(f"{p['name']} (Priority: HIGH)")
                lbl.setStyleSheet("color: #00FFFF; font-size: 12px; border: none;")
                bar = QProgressBar()
                bar.setValue(p['progress'])
                bar.setStyleSheet("QProgressBar { height: 6px; background: #111; border: none; } QProgressBar::chunk { background: #00FFFF; }")
                bar.setTextVisible(False)
                self.obj_layout.addWidget(lbl)
                self.obj_layout.addWidget(bar)
                
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
                status = "✔" if t['done'] else "○"
                color = "#00FF00" if t['done'] else "#FFFF00"
                lbl = QLabel(f"{status} [{t['section'].upper()}] {t['text']}")
                lbl.setStyleSheet(f"color: {color}; font-size: 12px; border: none; padding: 2px;")
                self.timeline_layout.addWidget(lbl)
        
        self.timeline_layout.addStretch()
