import streamlit as st
from pawpal_system import Owner, Pet, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

# --- Owner registry ---
if "owners" not in st.session_state:
    st.session_state.owners = {}

st.subheader("Add Owner")
with st.form("add_owner_form"):
    owner_name = st.text_input("Owner name", value="Jordan")
    pet_name = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "other"])
    submitted = st.form_submit_button("Add owner")

if submitted:
    if not owner_name:
        st.warning("Owner name cannot be empty.")
    elif owner_name in st.session_state.owners:
        st.warning(f"'{owner_name}' already exists.")
    else:
        pet = Pet(name=pet_name, species=species)
        new_owner = Owner(name=owner_name)
        new_owner.add_pet(pet)
        st.session_state.owners[owner_name] = new_owner
        st.success(f"Added owner '{owner_name}' with pet '{pet_name}'.")

st.divider()

if not st.session_state.owners:
    st.info("No owners yet. Add one above.")
    st.stop()

# --- Owner selector ---
st.subheader("Select Owner")
selected_name = st.selectbox("Owner", list(st.session_state.owners.keys()))
owner = st.session_state.owners[selected_name]
pet = owner.pets[0]

st.caption(f"Pet: **{pet.name}** ({pet.species})")

# --- Tasks ---
st.markdown("### Tasks")
st.caption("Add tasks to build a schedule.")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    task = Task(title=task_title, duration=int(duration), priority=priority, pet=pet)
    owner.schedule.add_task(task)

if owner.schedule.tasks:
    st.write("Current tasks:")
    st.table([
        {"title": t.title, "duration_minutes": t.duration, "priority": t.priority}
        for t in owner.schedule.tasks
    ])
else:
    st.info("No tasks yet. Add one above.")

st.divider()

# --- Schedule ---
st.subheader("Build Schedule")
available_minutes = st.number_input("Available minutes today", min_value=10, max_value=480, value=60)

if st.button("Generate schedule"):
    plan_text = owner.schedule.explain_plan(available_minutes=int(available_minutes))
    st.text(plan_text)
