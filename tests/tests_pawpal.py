import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from pawpal_system import Pet, Task


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
