from dataclasses import dataclass, field

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
        if task.pet not in self.owner.pets:
            raise ValueError(
                f"Pet '{task.pet.name}' does not belong to owner '{self.owner.name}'"
            )
        self.tasks.append(task)
        if task not in task.pet.tasks:
            task.pet.tasks.append(task)

    def get_schedule(self) -> list[Task]:
        """Return all incomplete tasks sorted by priority then title."""
        pending = [t for t in self.tasks if not t.completed]
        return sorted(pending, key=lambda t: (PRIORITY_ORDER.get(t.priority, 99), t.title))

    def get_tasks_for_pet(self, pet: Pet) -> list[Task]:
        """Return incomplete tasks for a specific pet, sorted by priority."""
        return [t for t in self.get_schedule() if t.pet is pet]

    def get_tasks_by_priority(self, priority: str) -> list[Task]:
        """Return all incomplete tasks matching the given priority level."""
        return [t for t in self.get_schedule() if t.priority == priority]

    def complete_task(self, task: Task) -> None:
        """Mark a task as completed."""
        task.complete()

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
