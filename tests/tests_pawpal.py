import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from datetime import date, timedelta
import pytest
from pawpal_system import Owner, Pet, Task


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_owner_with_pet(owner_name="Alex", pet_name="Buddy", species="dog"):
    owner = Owner(owner_name)
    pet = Pet(name=pet_name, species=species)
    owner.add_pet(pet)
    return owner, pet


# ---------------------------------------------------------------------------
# Original tests (kept)
# ---------------------------------------------------------------------------

def test_task_completion_changes_status():
    pet = Pet(name="Buddy", species="dog")
    task = Task(title="Walk", duration=30, priority="high", pet=pet)

    assert task.completed is False
    task.complete()
    assert task.completed is True


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Whiskers", species="cat")
    assert len(pet.tasks) == 0

    task = Task(title="Feed", duration=5, priority="medium", pet=pet)
    pet.add_task(task)
    assert len(pet.tasks) == 1


# ---------------------------------------------------------------------------
# Sorting correctness: chronological order (get_schedule_by_time)
# ---------------------------------------------------------------------------

def test_get_schedule_by_time_returns_chronological_order():
    owner, pet = make_owner_with_pet()
    afternoon = Task(title="Groom", duration=20, priority="low", pet=pet, time="14:00")
    morning   = Task(title="Walk",  duration=30, priority="high", pet=pet, time="08:00")
    midday    = Task(title="Feed",  duration=5,  priority="medium", pet=pet, time="12:00")
    for t in (afternoon, morning, midday):
        owner.schedule.add_task(t)

    result = owner.schedule.get_schedule_by_time()
    assert [t.time for t in result] == ["08:00", "12:00", "14:00"]


def test_get_schedule_by_time_tasks_without_time_go_last():
    owner, pet = make_owner_with_pet()
    no_time = Task(title="Brush", duration=10, priority="high", pet=pet, time="")
    timed   = Task(title="Walk",  duration=30, priority="low",  pet=pet, time="07:00")
    for t in (no_time, timed):
        owner.schedule.add_task(t)

    result = owner.schedule.get_schedule_by_time()
    assert result[0].title == "Walk"
    assert result[-1].title == "Brush"


def test_get_schedule_priority_tiebreak_by_title():
    owner, pet = make_owner_with_pet()
    task_z = Task(title="Zzz Nap",  duration=10, priority="high", pet=pet)
    task_a = Task(title="Alpha Run", duration=10, priority="high", pet=pet)
    for t in (task_z, task_a):
        owner.schedule.add_task(t)

    result = owner.schedule.get_schedule()
    assert result[0].title == "Alpha Run"
    assert result[1].title == "Zzz Nap"


# ---------------------------------------------------------------------------
# Recurrence logic: daily and weekly
# ---------------------------------------------------------------------------

def test_complete_daily_task_creates_next_day_occurrence():
    owner, pet = make_owner_with_pet()
    today = date.today()
    task = Task(title="Walk", duration=30, priority="high", pet=pet,
                frequency="daily", due_date=today)
    owner.schedule.add_task(task)

    owner.schedule.complete_task(task)

    pending = owner.schedule.get_schedule(status="pending")
    assert len(pending) == 1
    assert pending[0].due_date == today + timedelta(days=1)
    assert pending[0].title == "Walk"


def test_complete_weekly_task_creates_next_week_occurrence():
    owner, pet = make_owner_with_pet()
    today = date.today()
    task = Task(title="Bath", duration=45, priority="medium", pet=pet,
                frequency="weekly", due_date=today)
    owner.schedule.add_task(task)

    owner.schedule.complete_task(task)

    pending = owner.schedule.get_schedule(status="pending")
    assert len(pending) == 1
    assert pending[0].due_date == today + timedelta(weeks=1)


def test_complete_non_recurring_task_does_not_reschedule():
    owner, pet = make_owner_with_pet()
    task = Task(title="Vet Visit", duration=60, priority="high", pet=pet,
                frequency="as needed")
    owner.schedule.add_task(task)

    owner.schedule.complete_task(task)

    pending = owner.schedule.get_schedule(status="pending")
    assert len(pending) == 0


def test_complete_daily_task_without_due_date_uses_today():
    owner, pet = make_owner_with_pet()
    task = Task(title="Walk", duration=30, priority="high", pet=pet,
                frequency="daily")  # no due_date set
    owner.schedule.add_task(task)

    owner.schedule.complete_task(task)

    pending = owner.schedule.get_schedule(status="pending")
    assert len(pending) == 1
    assert pending[0].due_date == date.today() + timedelta(days=1)


def test_recurrence_inherits_all_properties():
    owner, pet = make_owner_with_pet()
    today = date.today()
    task = Task(title="Walk", duration=30, priority="high", pet=pet,
                description="Leash walk around the block", time="08:00",
                frequency="daily", due_date=today)
    owner.schedule.add_task(task)

    owner.schedule.complete_task(task)

    next_task = owner.schedule.get_schedule(status="pending")[0]
    assert next_task.title == "Walk"
    assert next_task.duration == 30
    assert next_task.priority == "high"
    assert next_task.description == "Leash walk around the block"
    assert next_task.time == "08:00"
    assert next_task.frequency == "daily"


# ---------------------------------------------------------------------------
# Conflict detection
# ---------------------------------------------------------------------------

def test_get_conflicts_flags_duplicate_time_slot():
    owner, pet = make_owner_with_pet()
    t1 = Task(title="Walk", duration=30, priority="high",   pet=pet, time="08:00")
    t2 = Task(title="Feed", duration=5,  priority="medium", pet=pet, time="08:00")
    for t in (t1, t2):
        owner.schedule.add_task(t)

    conflicts = owner.schedule.get_conflicts()
    assert "08:00" in conflicts
    assert len(conflicts["08:00"]) == 2


def test_get_conflicts_different_times_no_conflict():
    owner, pet = make_owner_with_pet()
    t1 = Task(title="Walk", duration=30, priority="high",   pet=pet, time="08:00")
    t2 = Task(title="Feed", duration=5,  priority="medium", pet=pet, time="09:00")
    for t in (t1, t2):
        owner.schedule.add_task(t)

    assert owner.schedule.get_conflicts() == {}


def test_get_conflicts_ignores_tasks_without_time():
    owner, pet = make_owner_with_pet()
    t1 = Task(title="Brush", duration=10, priority="low", pet=pet, time="")
    t2 = Task(title="Nap",   duration=60, priority="low", pet=pet, time="")
    for t in (t1, t2):
        owner.schedule.add_task(t)

    assert owner.schedule.get_conflicts() == {}


def test_warn_conflicts_returns_warning_strings():
    owner, pet = make_owner_with_pet()
    t1 = Task(title="Walk", duration=30, priority="high",   pet=pet, time="08:00")
    t2 = Task(title="Feed", duration=5,  priority="medium", pet=pet, time="08:00")
    for t in (t1, t2):
        owner.schedule.add_task(t)

    warnings = owner.schedule.warn_conflicts()
    assert len(warnings) == 1
    assert "08:00" in warnings[0]
    assert "WARNING" in warnings[0]


def test_add_task_raises_for_unowned_pet():
    owner = Owner("Alex")
    stranger_pet = Pet(name="Stranger", species="cat")  # never added to owner
    task = Task(title="Feed", duration=5, priority="low", pet=stranger_pet)

    with pytest.raises(ValueError):
        owner.schedule.add_task(task)


def test_conflict_across_different_pets_same_time():
    owner = Owner("Alex")
    dog = Pet(name="Buddy", species="dog")
    cat = Pet(name="Whiskers", species="cat")
    owner.add_pet(dog)
    owner.add_pet(cat)

    t1 = Task(title="Walk",      duration=30, priority="high",   pet=dog, time="09:00")
    t2 = Task(title="Cat Brush", duration=10, priority="medium", pet=cat, time="09:00")
    owner.schedule.add_task(t1)
    owner.schedule.add_task(t2)

    conflicts = owner.schedule.get_conflicts()
    assert "09:00" in conflicts
