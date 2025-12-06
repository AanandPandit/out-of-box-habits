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
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        for d in dates:
            day = self.habits_manager.data[d]
            
            protocols_completed = 0
            for section in ['protocols', 'main', 'outreach']:
                tasks = day.get(section, [])
                for t in tasks:
                    if t.get('done', False):
                        completed += 1
                        if section == 'protocols':
                            protocols_completed += 1
                    elif d < today_str:
                        missed += 1
            
            trend.append({
                "date": d,
                "productivity": day.get('productivity', 0),
                "mood": day.get('mood', 0),
                "completed": completed,
                "missed": missed,
                "protocols_completed": protocols_completed
            })
        return trend

    def get_missed_tasks_count(self, date_str):
        day = self.habits_manager.get_day(date_str)
        missed = 0
        for section in ['protocols', 'main', 'outreach']:
            tasks = day.get(section, [])
            # Assuming if not done and it's a past date, it's missed.
            # For today, it's just pending.
            # But the requirement asks for "missed" tasks today? Usually missed means past deadline.
            # For "Daily Task Performance Panel", "missed" might mean tasks explicitly marked as failed or not done by end of day?
            # Let's assume for today, missed is 0 unless we have a specific "failed" status.
            # But for past days, not done = missed.
            if date_str < datetime.now().strftime("%Y-%m-%d"):
                missed += sum(1 for t in tasks if not t.get('done', False))
        return missed

    def get_weekly_breakdown(self):
        # Last 7 days
        dates = sorted(self.habits_manager.data.keys())[-7:]
        completed = 0
        missed = 0
        pending = 0 # Only for today
        
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        for d in dates:
            day = self.habits_manager.data[d]
            for section in ['protocols', 'main', 'outreach']:
                tasks = day.get(section, [])
                for t in tasks:
                    if t.get('done', False):
                        completed += 1
                    elif d < today_str:
                        missed += 1
                    elif d == today_str:
                        pending += 1
                        
        return {"completed": completed, "missed": missed, "pending": pending}

    def get_improvement_rate(self):
        today_str = datetime.now().strftime("%Y-%m-%d")
        yesterday_str = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        
        today_comp = self.get_daily_completion(today_str)
        yesterday_comp = self.get_daily_completion(yesterday_str)
        
        if yesterday_comp == 0:
            return 100 if today_comp > 0 else 0
            
        return ((today_comp - yesterday_comp) / yesterday_comp) * 100
