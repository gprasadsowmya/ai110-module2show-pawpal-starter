# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

The `Schedule` class was extended with four algorithmic improvements:

**Sort by time** — `get_schedule_by_time(status)` returns tasks ordered chronologically by their `HH:MM` start time. Tasks with no time set are pushed to the end. Accepts the same `status` filter as `get_schedule()`.

**Filter by status** — `get_schedule(status)` now accepts `"pending"` (default), `"completed"`, or `"all"`, replacing the previous hard-coded pending-only filter. `get_tasks_for_pet()` and `get_tasks_by_priority()` expose the same parameter.

**Automatic recurring tasks** — `complete_task()` checks the completed task's `frequency`. For `"daily"` tasks it creates a new occurrence due tomorrow (`timedelta(days=1)`); for `"weekly"` tasks it schedules one seven days out (`timedelta(weeks=1)`). Monthly and one-off tasks are not auto-rescheduled.

**Conflict detection** — `add_task()` prints a live warning whenever a new task lands on an already-occupied time slot. `get_conflicts()` returns a dict of every double-booked slot, and `warn_conflicts()` formats those into plain warning strings. Detection is exact start-time matching — a deliberate tradeoff documented in `reflection.md`.

---

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
