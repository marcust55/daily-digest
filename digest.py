import anthropic
from data import load_data, get_today_classes, get_upcoming_quizzes

client = anthropic.Anthropic()

data = load_data()
today_classes = get_today_classes(data)
upcoming = get_upcoming_quizzes(data)

prompt = f"""
Here is my schedule for today: {today_classes}
Here are my upcoming quizzes: {upcoming}

Write a short, motivating daily digest. Include:
1. What classes I have today
2. What quizzes are coming up, ranked by urgency
3. One specific recommendation for what I should study first today
"""

response = client.messages.create(
    model="claude-sonnet-5",
    max_tokens=500,
    messages=[{"role": "user", "content": prompt}]
)

for block in response.content:
    if block.type == "text":
        print(block.text)