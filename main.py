from pawpal_system import Owner, Pet, Task

# --- Setup ---
owner = Owner("Jordan")

mochi = Pet(name="Mochi", species="cat")
biscuit = Pet(name="Biscuit", species="dog")

owner.add_pet(mochi)
owner.add_pet(biscuit)

# --- Tasks added intentionally OUT OF ORDER ---
# (latest times first, mixed pets, mixed priorities)

owner.schedule.add_task(Task(
    title="Evening feeding",
    duration=10,
    priority="high",
    pet=mochi,
    description="Wet food + fresh water",
    time="18:00",
    frequency="daily",
))

owner.schedule.add_task(Task(
    title="Flea treatment",
    duration=5,
    priority="low",
    pet=biscuit,
    description="Apply monthly topical treatment",
    time="08:00",       # conflicts with Morning walk intentionally
    frequency="monthly",
))

owner.schedule.add_task(Task(
    title="Training session",
    duration=20,
    priority="medium",
    pet=biscuit,
    description="Sit, stay, recall — 5 min break between sets",
    time="10:30",
    frequency="daily",
))

owner.schedule.add_task(Task(
    title="Morning walk",
    duration=30,
    priority="high",
    pet=biscuit,
    description="At least 2 blocks, off-leash at the park if possible",
    time="08:00",       # same time as Flea treatment — deliberate conflict
    frequency="daily",
))

owner.schedule.add_task(Task(
    title="Brush coat",
    duration=15,
    priority="medium",
    pet=mochi,
    description="Use fine-tooth comb to reduce shedding",
    time="09:00",
    frequency="daily",
))

owner.schedule.add_task(Task(
    title="Morning feeding",
    duration=10,
    priority="high",
    pet=mochi,
    description="Wet food + fresh water",
    time="07:00",
    frequency="daily",
))

# --- Mark one task completed so filter-by-status has something to show ---
owner.schedule.complete_task(owner.schedule.tasks[2])   # Training session

# ── 1. SORT BY TIME ────────────────────────────────────────────────────────────
print("=" * 55)
print("1. TASKS SORTED BY TIME (pending only)")
print("=" * 55)
for t in owner.schedule.get_schedule_by_time():
    print(f"  {t.time or '--:--'}  [{t.priority.upper():6}]  {t.title:<22}  ({t.pet.name})")

# ── 2. FILTER BY STATUS ────────────────────────────────────────────────────────
print()
print("=" * 55)
print("2a. FILTER: pending tasks")
print("=" * 55)
for t in owner.schedule.get_schedule(status="pending"):
    print(f"  [{t.priority.upper():6}]  {t.title:<22}  ({t.pet.name})")

print()
print("=" * 55)
print("2b. FILTER: completed tasks")
print("=" * 55)
completed = owner.schedule.get_schedule(status="completed")
if completed:
    for t in completed:
        print(f"  [{t.priority.upper():6}]  {t.title:<22}  ({t.pet.name})")
else:
    print("  (none)")

print()
print("=" * 55)
print("2c. FILTER: all tasks")
print("=" * 55)
for t in owner.schedule.get_schedule(status="all"):
    done = "[DONE]" if t.completed else "      "
    print(f"  {done}  [{t.priority.upper():6}]  {t.title:<22}  ({t.pet.name})")

# ── 3. CONFLICT DETECTION ──────────────────────────────────────────────────────
print()
print("=" * 55)
print("3. CONFLICT DETECTION")
print("=" * 55)
conflicts = owner.schedule.get_conflicts()
if conflicts:
    for time_slot, tasks in conflicts.items():
        print(f"  CONFLICT at {time_slot}:")
        for t in tasks:
            print(f"    - {t.title} ({t.pet.name})")
else:
    print("  No conflicts found.")
