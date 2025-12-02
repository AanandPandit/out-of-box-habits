from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QLineEdit, QPushButton, QLabel, QFrame, QGraphicsOpacityEffect)
from PyQt5.QtCore import Qt, QPropertyAnimation, QPoint, QSize, QThread, pyqtSignal
from python.perplexity_chatbot import ask_perplexity

class ChatWorker(QThread):
    finished = pyqtSignal(str)
    
    def __init__(self, prompt, history):
        super().__init__()
        self.prompt = prompt
        self.history = history
        
    def run(self):
        response = ask_perplexity(self.prompt, self.history)
        self.finished.emit(response)

class ChatbotPanel(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedWidth(400)
        self.setStyleSheet("background-color: #050505; border-right: 1px solid #00FF00;")
        
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel(">> PERPLEXITY_UPLINK")
        header.setStyleSheet("font-weight: bold; color: #00FFFF; font-size: 16px; padding: 10px;")
        layout.addWidget(header)
        
        # Chat History
        self.history_display = QTextEdit()
        self.history_display.setReadOnly(True)
        self.history_display.setStyleSheet("border: none; background-color: transparent; font-family: 'Consolas'; font-size: 14px;")
        layout.addWidget(self.history_display)
        
        # Input Area
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter command...")
        self.input_field.setStyleSheet("font-family: 'Consolas'; font-size: 14px; background-color: #050505; border: 1px solid #003300; color: #00FF00; padding: 5px;")
        self.input_field.returnPressed.connect(self.send_message)
        
        self.send_btn = QPushButton("SEND")
        self.send_btn.clicked.connect(self.send_message)
        
        input_layout.addWidget(self.input_field)
        input_layout.addWidget(self.send_btn)
        layout.addLayout(input_layout)
        
        self.chat_history = []
        self.worker = None

    def send_message(self):
        text = self.input_field.text().strip()
        if not text: return
        
        self.append_message("USER", text)
        self.input_field.clear()
        self.input_field.setDisabled(True)
        
        self.worker = ChatWorker(text, self.chat_history)
        self.worker.finished.connect(self.handle_response)
        self.worker.start()
        
    def handle_response(self, response):
        self.append_message("AI", response)
        self.chat_history.append({"role": "assistant", "content": response})
        self.input_field.setDisabled(False)
        self.input_field.setFocus()
        
    def append_message(self, sender, text):
        # User requested Neon Blue for AI (or chatbot in general). 
        # I'll use Neon Blue (#00FFFF) for AI and Green (#00FF00) for User to contrast, 
        # or vice versa based on standard hacker tropes.
        # Prompt said: "use the color neon blue... for perplexity chat bot"
        color = "#00FFFF" if sender == "AI" else "#00FF00" 
        formatted = f'<div style="margin-bottom: 10px;"><b style="color: {color};">[{sender}]:</b> <span style="color: #EEEEEE;">{text}</span></div>'
        self.history_display.append(formatted)
        if sender == "USER":
             self.chat_history.append({"role": "user", "content": text})
