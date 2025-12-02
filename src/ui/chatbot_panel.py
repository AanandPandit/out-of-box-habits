from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QTextEdit, 
                             QLineEdit, QPushButton, QLabel, QFrame, QGraphicsOpacityEffect)
from PyQt5.QtCore import Qt, QPropertyAnimation, QPoint, QSize, QThread, pyqtSignal
from python.perplexity_chatbot import ask_perplexity
import json
import os
import markdown

CHAT_HISTORY_FILE = "data/chat_history.json"

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
        
        self.load_history()

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
        self.save_history()
        self.input_field.setDisabled(False)
        self.input_field.setFocus()
        
    def append_message(self, sender, text):
        color = "#00FFFF" if sender == "AI" else "#00FF00"
        
        if sender == "AI":
            # Render Markdown
            try:
                # Convert markdown to html
                html_content = markdown.markdown(text, extensions=['fenced_code', 'nl2br', 'tables', 'sane_lists'])
                
                # Basic Math handling: Replace $...$ with italic or bold for visibility if markdown didn't catch it
                # Note: This is a hack because QTextEdit doesn't support MathML/LaTeX
                # We'll just ensure it's visible.
                # html_content = html_content.replace('$', '<span style="color:#FF00FF;">$</span>')
                
                formatted = f'<div style="margin-bottom: 20px;"><b style="color: {color};">[{sender}]:</b><br><div style="color: #EEEEEE; margin-top: 5px;">{html_content}</div></div>'
            except Exception as e:
                # Fallback
                formatted = f'<div style="margin-bottom: 20px;"><b style="color: {color};">[{sender}]:</b> <span style="color: #EEEEEE;">{text}</span></div>'
        else:
            # User message (keep simple)
            formatted = f'<div style="margin-bottom: 10px;"><b style="color: {color};">[{sender}]:</b> <span style="color: #EEEEEE;">{text}</span></div>'
            
        self.history_display.append(formatted)
        if sender == "USER":
             self.chat_history.append({"role": "user", "content": text})
        self.save_history()

    def save_history(self):
        try:
            if not os.path.exists("data"):
                os.makedirs("data")
            # Save both the raw messages and the display html if needed, but here we just save the message objects
            # To restore the UI, we'll need to re-render them.
            with open(CHAT_HISTORY_FILE, 'w') as f:
                json.dump(self.chat_history, f)
        except Exception as e:
            print(f"Error saving chat history: {e}")

    def load_history(self):
        if os.path.exists(CHAT_HISTORY_FILE):
            try:
                with open(CHAT_HISTORY_FILE, 'r') as f:
                    self.chat_history = json.load(f)
                    for msg in self.chat_history:
                        role = msg['role']
                        content = msg['content']
                        sender = "AI" if role == "assistant" else "USER"
                        # Don't append to self.chat_history again inside append_message
                        color = "#00FFFF" if sender == "AI" else "#00FF00" 
                        formatted = f'<div style="margin-bottom: 10px;"><b style="color: {color};">[{sender}]:</b> <span style="color: #EEEEEE;">{content}</span></div>'
                        self.history_display.append(formatted)
            except Exception as e:
                print(f"Error loading chat history: {e}")
