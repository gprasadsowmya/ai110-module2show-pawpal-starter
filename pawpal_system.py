from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}


@dataclass
class Pet:
    name: str
    species: str = "unknown"
    owner: "Owner | None" = field(default=None, repr=False)
    tasks: list["Task"] = field(default_factory=list, repr=False)

    def add_task(self, task: "Task") -> None:
        task.pet = self
        self.tasks.append(task)


@dataclass
class Task:
    title: str
    duration: int          # minutes
    priority: str          # "high", "medium", or "low"
    pet: Pet
    description: str = ""
    time: str = ""         # e.g. "08:00"
    frequency: str = "daily"  # e.g. "daily", "weekly", "as needed"
    completed: bool = False
    due_date: date | None = None

    def complete(self) -> None:
        self.completed = True


class Owner:
    def __init__(self, name: str):
        self.name = name
        self.pets: list[Pet] = []
        self.schedule: "Schedule" = Schedule(self)

    def add_pet(self, pet: Pet) -> None:
        pet.owner = self
        self.pets.append(pet)

    def get_all_tasks(self) -> list[Task]:
        """Return every task across all owned pets."""
        tasks: list[Task] = []
        for pet in self.pets:
            tasks.extend(pet.tasks)
        return tasks


class Schedule:
    """The scheduling 'brain': retrieves, organizes, and manages tasks across pets."""

    def __init__(self, owner: Owner):
        self.owner = owner
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        """Add a task to this schedule and sync it to the pet's task list.

        Performs a lightweight conflict check before adding: if another task is
        already scheduled at the same time, a warning is printed to stdout but
        the task is still added. The program never crashes on a conflict.

        Args:
            task: The Task to add. Its ``pet`` must already belong to this
                schedule's owner, otherwise a ValueError is raised.

        Raises:
            ValueError: If ``task.pet`` is not in ``self.owner.pets``.
        """
        if task.pet not in self.owner.pets:
            raise ValueError(
                f"Pet '{task.pet.name}' does not belong to owner '{self.owner.name}'"
            )
        # Lightweight conflict check — warn but never crash
        if task.time:
            clashes = [t for t in self.tasks if t.time == task.time]
            for clash in clashes:
                print(
                    f"WARNING: '{task.title}' ({task.pet.name}) conflicts with "
                    f"'{clash.title}' ({clash.pet.name}) — both scheduled at {task.time}"
                )
        self.tasks.append(task)
        if task not in task.pet.tasks:
            task.pet.tasks.append(task)

    def get_schedule(self, status: str = "pending") -> list[Task]:
        """Return tasks sorted by priority then title.

        status: "pending" (default) — incomplete only
                "completed"          — completed only
                "all"                — every task
        """
        if status == "completed":
            tasks = [t for t in self.tasks if t.completed]
        elif status == "all":
            tasks = self.tasks[:]
        else:
            tasks = [t for t in self.tasks if not t.completed]
        return sorted(tasks, key=lambda t: (PRIORITY_ORDER.get(t.priority, 99), t.title))

    def get_schedule_by_time(self, status: str = "pending") -> list[Task]:
        """Return tasks sorted chronologically by their scheduled start time.

        Relies on ``get_schedule()`` for filtering, then re-sorts by the
        ``time`` field (a ``"HH:MM"`` string). Tasks with no time value are
        pushed to the end of the list using the sentinel ``"99:99"``.

        Args:
            status: Which tasks to include — ``"pending"`` (default),
                ``"completed"``, or ``"all"``.

        Returns:
            A list of Task objects ordered by start time, earliest first.
        """
        tasks = self.get_schedule(status=status)
        return sorted(tasks, key=lambda t: t.time if t.time else "99:99")

    def get_conflicts(self) -> dict[str, list[Task]]:
        """Return a dict of time slots that have more than one task scheduled.

        Keys are time strings (e.g. "08:00"); values are the conflicting Task lists.
        Only tasks with a non-empty time value are considered.
        """
        time_map: dict[str, list[Task]] = defaultdict(list)
        for t in self.tasks:
            if t.time:
                time_map[t.time].append(t)
        return {time: tasks for time, tasks in time_map.items() if len(tasks) > 1}

    def warn_conflicts(self) -> list[str]:
        """Return human-readable warning strings for every double-booked time slot.

        Wraps ``get_conflicts()`` and formats each conflicting slot as a plain
        string. Never raises an exception — an empty list means no conflicts.

        Returns:
            A list of warning strings, one per conflicting time slot. Each
            string identifies the slot and names all tasks scheduled there,
            e.g. ``"WARNING: 2 tasks overlap at 08:00 — 'Walk' (Biscuit), ..."``.
            Returns an empty list when there are no conflicts.
        """
        warnings = []
        for time_slot, tasks in self.get_conflicts().items():
            names = ", ".join(f"'{t.title}' ({t.pet.name})" for t in tasks)
            warnings.append(
                f"WARNING: {len(tasks)} tasks overlap at {time_slot} — {names}"
            )
        return warnings

    def get_tasks_for_pet(self, pet: Pet, status: str = "pending") -> list[Task]:
        """Return tasks for a specific pet, sorted by priority."""
        return [t for t in self.get_schedule(status=status) if t.pet is pet]

    def get_tasks_by_priority(self, priority: str, status: str = "pending") -> list[Task]:
        """Return tasks matching the given priority level."""
        return [t for t in self.get_schedule(status=status) if t.priority == priority]

    def complete_task(self, task: Task) -> None:
        """Mark a task as completed and auto-schedule the next occurrence if recurring.

        Calls ``task.complete()`` to set the completed flag, then checks the
        task's frequency. For ``"daily"`` tasks the next occurrence is due
        tomorrow (``timedelta(days=1)``); for ``"weekly"`` tasks it is due in
        seven days (``timedelta(weeks=1)``). All other frequencies
        (``"monthly"``, ``"as needed"``, etc.) are left as-is — no new task
        is created.

        If the completed task has no ``due_date`` set, ``date.today()`` is
        used as the base so the calculation never errors on older tasks.

        Args:
            task: The Task to mark as done. Must already be present in this
                schedule's task list.
        """
        task.complete()
        if task.frequency in ("daily", "weekly"):
            delta = timedelta(days=1) if task.frequency == "daily" else timedelta(weeks=1)
            next_task = Task(
                title=task.title,
                duration=task.duration,
                priority=task.priority,
                pet=task.pet,
                description=task.description,
                time=task.time,
                frequency=task.frequency,
                due_date=(task.due_date or date.today()) + delta,
            )
            self.add_task(next_task)

    def get_daily_plan(self, available_minutes: int) -> list[Task]:
        """
        Build a day plan: pick highest-priority tasks that fit within
        the available time budget. Returns the selected tasks in order.
        """
        plan: list[Task] = []
        remaining = available_minutes
        for task in self.get_schedule():
            if task.duration <= remaining:
                plan.append(task)
                remaining -= task.duration
        return plan

    def explain_plan(self, available_minutes: int) -> str:
        """Return a human-readable explanation of the daily plan."""
        plan = self.get_daily_plan(available_minutes)
        if not plan:
            return "No tasks fit within the available time."

        lines = [f"Daily plan for {self.owner.name} ({available_minutes} min available):\n"]
        for i, task in enumerate(plan, 1):
            lines.append(
                f"  {i}. [{task.priority.upper()}] {task.title} "
                f"({task.duration} min) — {task.pet.name}"
            )
            if task.description:
                lines.append(f"     {task.description}")
        total = sum(t.duration for t in plan)
        lines.append(f"\nTotal time: {total} min  |  Tasks scheduled: {len(plan)}")
        return "\n".join(lines)
