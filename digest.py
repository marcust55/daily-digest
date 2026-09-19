"""Daily Digest: reads a course schedule and asks an LLM for a prioritized study plan."""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path


@dataclass(frozen=True)
class ClassSession:
    name: str
    days: tuple
    time: str

    def meets_on(self, weekday: str) -> bool:
        return weekday in self.days


@dataclass(frozen=True)
class Assignment:
    course: str
    name: str
    due: date
    status: str = "not_started"

    def days_left(self, today: date) -> int:
        return (self.due - today).days

    def is_open(self) -> bool:
        return self.status != "done"


class Schedule:
    """Owns the schedule data and hides the JSON format from everything else."""

    def __init__(self, classes, assignments):
        self._classes = list(classes)
        self._assignments = list(assignments)

    @classmethod
    def from_json(cls, path):
        with open(path) as f:
            raw = json.load(f)
        classes = [
            ClassSession(
                c["name"],
                tuple(d.strip() for d in c["day"].split(",")),
                c["time"],
            )
            for c in raw["classes"]
        ]
        assignments = [
            Assignment(
                q["course"],
                q["name"],
                datetime.strptime(q["due"], "%Y-%m-%d").date(),
                q.get("status", "not_started"),
            )
            for q in raw["quizzes"]
        ]
        return cls(classes, assignments)

    def classes_on(self, day: date):
        weekday = day.strftime("%A")
        return [c for c in self._classes if c.meets_on(weekday)]

    def upcoming(self, today: date, days_ahead: int = 7):
        cutoff = today + timedelta(days=days_ahead)
        due_soon = [
            a for a in self._assignments
            if a.is_open() and today <= a.due <= cutoff
        ]
        return sorted(due_soon, key=lambda a: a.due)


class LLMClient(ABC):
    """Interface: anything that turns a prompt into text."""

    @abstractmethod
    def generate(self, prompt: str) -> str: ...


class ClaudeClient(LLMClient):
    def __init__(self, model: str = "claude-sonnet-5", max_tokens: int = 500):
        import anthropic

        self._client = anthropic.Anthropic()
        self._model = model
        self._max_tokens = max_tokens

    def generate(self, prompt: str) -> str:
        response = self._client.messages.create(
            model=self._model,
            max_tokens=self._max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(b.text for b in response.content if b.type == "text")


class FakeClient(LLMClient):
    """Test double: records the prompt and returns canned text."""

    def __init__(self, reply: str = "fake digest"):
        self.reply = reply
        self.last_prompt = None

    def generate(self, prompt: str) -> str:
        self.last_prompt = prompt
        return self.reply


class DigestGenerator:
    """Builds the prompt from a Schedule and delegates text generation to a client."""

    def __init__(self, schedule: Schedule, client: LLMClient):
        self._schedule = schedule
        self._client = client

    def build_prompt(self, today: date) -> str:
        classes = self._schedule.classes_on(today)
        upcoming = self._schedule.upcoming(today)

        class_lines = "\n".join(f"- {c.name} ({c.time})" for c in classes) or "None"
        due_lines = "\n".join(
            f"- {a.course}: {a.name}, due {a.due} ({a.days_left(today)} days left)"
            for a in upcoming
        ) or "None"

        return (
            f"Today is {today:%A, %B %d, %Y}.\n\n"
            f"Classes today:\n{class_lines}\n\n"
            f"Due in the next 7 days:\n{due_lines}\n\n"
            "Write a short, motivating daily digest with:\n"
            "1. Today's classes (say so if there are none)\n"
            "2. Upcoming deadlines ranked by urgency (say so if there are none)\n"
            "3. One specific recommendation for what to study first today"
        )

    def generate(self, today: date) -> str:
        return self._client.generate(self.build_prompt(today))


def main():
    schedule = Schedule.from_json(Path(__file__).parent / "schedule.json")
    digest = DigestGenerator(schedule, ClaudeClient())
    print(digest.generate(date.today()))


if __name__ == "__main__":
    main()
