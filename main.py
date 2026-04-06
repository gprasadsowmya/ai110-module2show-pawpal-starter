from pawpal_system import Owner, Pet, Task

# --- Setup ---
owner = Owner("Jordan")

mochi = Pet(name="Mochi", species="cat")
biscuit = Pet(name="Biscuit", species="dog")

owner.add_pet(mochi)
owner.add_pet(biscuit)

# --- Tasks for Mochi ---
owner.schedule.add_task(Task(
    title="Morning feeding",
    duration=10,
    priority="high",
    pet=mochi,
    description="Wet food + fresh water",
    time="07:00",
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

# --- Tasks for Biscuit ---
owner.schedule.add_task(Task(
    title="Morning walk",
    duration=30,
    priority="high",
    pet=biscuit,
    description="At least 2 blocks, off-leash at the park if possible",
    time="08:00",
    frequency="daily",
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
    title="Flea treatment",
    duration=5,
    priority="low",
    pet=biscuit,
    description="Apply monthly topical treatment",
    time="11:00",
    frequency="monthly",
))

# --- Print Today's Schedule ---
print(owner.schedule.explain_plan(available_minutes=90))
