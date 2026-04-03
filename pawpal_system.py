from dataclasses import dataclass


@dataclass
class Pet:
    name: str


@dataclass
class Task:
    title: str
    duration: int
    priority: str
    pet: Pet


class Owner:
    def __init__(self, name: str):
        self.name = name
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        self.pets.append(pet)


class Schedule:
    def __init__(self, owner: Owner):
        self.owner = owner
        self.tasks: list[Task] = []

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def get_schedule(self) -> list[Task]:
        return self.tasks
