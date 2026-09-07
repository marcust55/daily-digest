import json
from datetime import datetime, timedelta

def load_data():
    with open("schedule.json") as f:
        return json.load(f)

def get_today_classes(data):
    today_name = datetime.now().strftime("%A")
    return [c for c in data["classes"] if c["day"] == today_name]

def get_upcoming_quizzes(data, days_ahead=7):
    today = datetime.now().date()
    cutoff = today + timedelta(days=days_ahead)
    upcoming = []
    for q in data["quizzes"]:
        due_date = datetime.strptime(q["due"], "%Y-%m-%d").date()
        if today <= due_date <= cutoff:
            upcoming.append(q)
    return sorted(upcoming, key=lambda x: x["due"])