import json
import os
import pandas as pd
from datetime import datetime

DATA_DIR = "data"
JSON_FILE = os.path.join(DATA_DIR, "habits.json")
EXCEL_FILE = os.path.join(DATA_DIR, "habits.xlsx")

class HabitsManager:
    def __init__(self):
        if not os.path.exists(DATA_DIR):
            os.makedirs(DATA_DIR)
        self.data = {}
        self.load_data()

    def load_data(self):
        if os.path.exists(JSON_FILE):
            try:
                with open(JSON_FILE, 'r') as f:
                    self.data = json.load(f)
            except Exception as e:
                print(f"Error loading habits: {e}")
        else:
            self.data = {}

    def save_data(self):
        try:
            with open(JSON_FILE, 'w') as f:
                json.dump(self.data, f, indent=4)
            self.export_to_excel()
        except Exception as e:
            print(f"Error saving habits: {e}")

    def get_day(self, date_str):
        if date_str not in self.data:
            # Initialize new day structure
            self.data[date_str] = {
                "protocols": [],
                "main": [],
                "gratitude": [],
                "lesson": "",
                "outreach": [],
                "mood": 5,
                "productivity": 5
            }
        return self.data[date_str]

    def update_day(self, date_str, day_data):
        self.data[date_str] = day_data
        self.save_data()

    def export_to_excel(self):
        # Flatten data for Excel
        rows = []
        for date, content in self.data.items():
            # Protocols
            for task in content.get('protocols', []):
                rows.append({"Date": date, "Section": "Protocols", "Task": task['text'], "Completed": task['done'], "Mood": content.get('mood'), "Productivity": content.get('productivity')})
            # Main
            for task in content.get('main', []):
                rows.append({"Date": date, "Section": "Main Tasks", "Task": task['text'], "Completed": task['done'], "Mood": content.get('mood'), "Productivity": content.get('productivity')})
            # Outreach
            for task in content.get('outreach', []):
                rows.append({"Date": date, "Section": "Outreach", "Task": task['text'], "Completed": task['done'], "Mood": content.get('mood'), "Productivity": content.get('productivity')})
            # Gratitude (stored as list of strings usually, but let's assume objects or strings)
            for item in content.get('gratitude', []):
                text = item['text'] if isinstance(item, dict) else item
                rows.append({"Date": date, "Section": "Gratitude", "Task": text, "Completed": True, "Mood": content.get('mood'), "Productivity": content.get('productivity')})
            # Lesson
            if content.get('lesson'):
                rows.append({"Date": date, "Section": "Lesson", "Task": content['lesson'], "Completed": True, "Mood": content.get('mood'), "Productivity": content.get('productivity')})

        if rows:
            df = pd.DataFrame(rows)
            df.to_excel(EXCEL_FILE, index=False)
