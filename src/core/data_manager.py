import json
import os
from datetime import datetime

DATA_FILE = "hacker_data.json"

class DataManager:
    def __init__(self):
        self.data = {
            "tasks": [],
            "projects": [],
            "future_plans": []
        }
        self.load_data()

    def load_data(self):
        if os.path.exists(DATA_FILE):
            try:
                with open(DATA_FILE, 'r') as f:
                    self.data = json.load(f)
            except Exception as e:
                print(f"Error loading data: {e}")

    def save_data(self):
        try:
            with open(DATA_FILE, 'w') as f:
                json.dump(self.data, f, indent=4)
        except Exception as e:
            print(f"Error saving data: {e}")

    # --- Tasks ---
    def add_task(self, title, due_date=None):
        task = {
            "id": int(datetime.now().timestamp() * 1000),
            "title": title,
            "due_date": due_date,
            "completed": False,
            "created_at": str(datetime.now())
        }
        self.data["tasks"].append(task)
        self.save_data()
        return task

    def get_tasks(self):
        return self.data["tasks"]

    def delete_task(self, task_id):
        self.data["tasks"] = [t for t in self.data["tasks"] if t["id"] != task_id]
        self.save_data()

    def toggle_task(self, task_id):
        for t in self.data["tasks"]:
            if t["id"] == task_id:
                t["completed"] = not t["completed"]
                break
        self.save_data()

    # --- Projects ---
    def add_project(self, name, description, deadline=None):
        project = {
            "id": int(datetime.now().timestamp() * 1000),
            "name": name,
            "description": description,
            "progress": 0,
            "tasks": [],
            "deadline": deadline,
            "completed": False
        }
        self.data["projects"].append(project)
        self.save_data()
        return project

    def toggle_project(self, project_id):
        for p in self.data["projects"]:
            if p["id"] == project_id:
                p["completed"] = not p.get("completed", False)
                # If completed, set progress to 100, else 0 (simplified)
                p["progress"] = 100 if p["completed"] else 0
                break
        self.save_data()

    def edit_project(self, project_id, name, deadline=None):
        for p in self.data["projects"]:
            if p["id"] == project_id:
                p["name"] = name
                p["deadline"] = deadline
                break
        self.save_data()

    def get_projects(self):
        return self.data["projects"]

    # --- Future Plans ---
    def add_plan(self, goal, category):
        plan = {
            "id": int(datetime.now().timestamp() * 1000),
            "goal": goal,
            "category": category,
            "notes": "",
            "done": False
        }
        self.data["future_plans"].append(plan)
        self.save_data()
        return plan

    def get_plans(self):
        return self.data["future_plans"]
