from src.core.habits_manager import HabitsManager
from datetime import datetime, timedelta

class StatsManager:
    def __init__(self):
        self.habits_manager = HabitsManager()

    def get_daily_completion(self, date_str):
        day = self.habits_manager.get_day(date_str)
        total = 0
        completed = 0
        
        for section in ['protocols', 'main', 'outreach']:
            tasks = day.get(section, [])
            total += len(tasks)
            completed += sum(1 for t in tasks if t.get('done', False))
            
        return (completed / total * 100) if total > 0 else 0

    def get_streak(self):
        # Simple streak: consecutive days with > 0 completion or specific logic
        # Here we assume streak means logging in and doing at least 1 task
        dates = sorted(self.habits_manager.data.keys(), reverse=True)
        streak = 0
        today = datetime.now().date()
        
        # Check if today is logged, if not check yesterday
        current_check = today
        
        for d_str in dates:
            d = datetime.strptime(d_str, "%Y-%m-%d").date()
            if d == current_check:
                streak += 1
                current_check -= timedelta(days=1)
            elif d < current_check:
                break # Gap found
                
        return streak

    def get_productivity_trend(self, days=7):
        dates = sorted(self.habits_manager.data.keys())[-days:]
        trend = []
        for d in dates:
            day = self.habits_manager.data[d]
            trend.append({
                "date": d,
                "productivity": day.get('productivity', 0),
                "mood": day.get('mood', 0)
            })
        return trend
