from data import load_data, get_today_classes, get_upcoming_quizzes

data = load_data()
print(get_today_classes(data))
print(get_upcoming_quizzes(data))