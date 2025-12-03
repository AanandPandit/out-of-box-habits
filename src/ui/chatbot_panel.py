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
        # Removed fixed width to allow resizing via QSplitter
        self.setMinimumWidth(300) 
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
        
    def set_online_status(self, is_online):
        if is_online:
            self.input_field.setEnabled(True)
            self.send_btn.setEnabled(True)
            self.input_field.setPlaceholderText("Enter command...")
            self.input_field.setStyleSheet("font-family: 'Consolas'; font-size: 14px; background-color: #050505; border: 1px solid #003300; color: #00FF00; padding: 5px;")
        else:
            self.input_field.setEnabled(False)
            self.send_btn.setEnabled(False)
            self.input_field.setPlaceholderText("⚠ OFFLINE - CONNECT TO INTERNET")
            self.input_field.setStyleSheet("font-family: 'Consolas'; font-size: 14px; background-color: #220000; border: 1px solid #FF0000; color: #FF0000; font-weight: bold; padding: 5px;")

    def send_message(self):
        text = self.input_field.text().strip()
        if not text: return
        
        self.append_message("USER", text)
        self.input_field.clear()
        self.input_field.setDisabled(True)
        self.show_loading()
        
        self.worker = ChatWorker(text, self.chat_history)
        self.worker.finished.connect(self.handle_response)
        self.worker.start()
        
    def handle_response(self, response):
        self.hide_loading()
        self.append_message("AI", response)
        self.chat_history.append({"role": "assistant", "content": response})
        self.save_history()
        self.input_field.setDisabled(False)
        self.input_field.setFocus()
        
    def show_loading(self):
        # Add a temporary loading message
        self.loading_msg = QLabel("AI IS THINKING...")
        self.loading_msg.setStyleSheet("color: #00FF00; font-style: italic; font-family: 'Consolas'; margin: 10px;")
        # We add it to the layout, but we need to be careful where. 
        # Actually, appending to history display is better for flow.
        self.history_display.append('<div style="color: #00FF00; font-style: italic;">>> UPLINK ESTABLISHED. PROCESSING...</div>')
        self.history_display.verticalScrollBar().setValue(self.history_display.verticalScrollBar().maximum())

    def hide_loading(self):
        # In a real text edit, we can't easily "remove" the last line without reloading.
        # But we can just leave the "Processing" log there as part of the hacker feel.
        # Or we can use a cursor. 
        # For now, let's just leave it as a log entry.
        pass

    def render_message(self, sender, text):
        color = "#00FFFF" if sender == "AI" else "#00FF00"
        
        if sender == "AI":
            # Render Markdown
            try:
                # Convert markdown to html
                html_content = markdown.markdown(text, extensions=['fenced_code', 'nl2br', 'tables', 'sane_lists'])
                formatted = f'<div style="margin-bottom: 20px;"><b style="color: {color};">[{sender}]:</b><br><div style="color: #EEEEEE; margin-top: 5px;">{html_content}</div></div>'
            except Exception as e:
                # Fallback
                formatted = f'<div style="margin-bottom: 20px;"><b style="color: {color};">[{sender}]:</b> <span style="color: #EEEEEE;">{text}</span></div>'
        else:
            # User message (keep simple)
            formatted = f'<div style="margin-bottom: 10px;"><b style="color: {color};">[{sender}]:</b> <span style="color: #EEEEEE;">{text}</span></div>'
        return formatted

    def append_message(self, sender, text):
        formatted = self.render_message(sender, text)
        self.history_display.append(formatted)
        if sender == "USER":
             self.chat_history.append({"role": "user", "content": text})
        self.save_history()

    def save_history(self):
        try:
            if not os.path.exists("data"):
                os.makedirs("data")
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
                        if role == "system": continue # Skip system prompt in display
                        sender = "AI" if role == "assistant" else "USER"
                        formatted = self.render_message(sender, content)
                        self.history_display.append(formatted)
            except Exception as e:
                print(f"Error loading chat history: {e}")
