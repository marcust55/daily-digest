from datetime import date
from pathlib import Path

from digest import DigestGenerator, FakeClient, Schedule

schedule = Schedule.from_json(Path(__file__).parent / "schedule.json")

MONDAY = date(2026, 5, 18)
SATURDAY = date(2026, 5, 23)


def test_classes_on_monday():
    names = [c.name for c in schedule.classes_on(MONDAY)]
    assert names == ["Linear Algebra - MATH 235", "Calculus - MATH 237"]


def test_no_classes_on_saturday():
    assert schedule.classes_on(SATURDAY) == []


def test_upcoming_sorted_and_windowed():
    upcoming = schedule.upcoming(MONDAY, days_ahead=7)
    assert [a.name for a in upcoming] == ["A1", "Quiz 1", "Quiz 1"]
    assert all(MONDAY <= a.due for a in upcoming)


def test_prompt_contains_schedule_and_calls_client():
    client = FakeClient("hello")
    result = DigestGenerator(schedule, client).generate(MONDAY)
    assert result == "hello"
    assert "MATH 235" in client.last_prompt
    assert "3 days left" in client.last_prompt


if __name__ == "__main__":
    for name, fn in list(globals().items()):
        if name.startswith("test_"):
            fn()
    print("all tests passed")
