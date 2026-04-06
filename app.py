import streamlit as st
from datetime import date
from pawpal_system import Owner, Pet, Task

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("🐾 PawPal+")
st.caption("A daily care planner for busy pet owners.")

# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------
if "owners" not in st.session_state:
    st.session_state.owners = {}

# ---------------------------------------------------------------------------
# Section 1: Add Owner + Pet
# ---------------------------------------------------------------------------
st.subheader("1. Register Owner & Pet")
with st.form("add_owner_form"):
    owner_name = st.text_input("Owner name", value="Jordan")
    pet_name   = st.text_input("Pet name",   value="Mochi")
    species    = st.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"])
    submitted  = st.form_submit_button("Add owner")

if submitted:
    if not owner_name.strip():
        st.warning("Owner name cannot be empty.")
    elif owner_name in st.session_state.owners:
        st.warning(f"'{owner_name}' already exists — select them below.")
    else:
        pet = Pet(name=pet_name.strip(), species=species)
        new_owner = Owner(name=owner_name.strip())
        new_owner.add_pet(pet)
        st.session_state.owners[owner_name] = new_owner
        st.success(f"Welcome, {owner_name}! Added pet **{pet_name}** ({species}).")

st.divider()

if not st.session_state.owners:
    st.info("No owners yet — add one above to get started.")
    st.stop()

# ---------------------------------------------------------------------------
# Section 2: Select Owner
# ---------------------------------------------------------------------------
st.subheader("2. Select Owner")
selected_name = st.selectbox("Owner", list(st.session_state.owners.keys()))
owner = st.session_state.owners[selected_name]
pet   = owner.pets[0]
st.caption(f"Active pet: **{pet.name}** ({pet.species})")

st.divider()

# ---------------------------------------------------------------------------
# Section 3: Add a Task
# ---------------------------------------------------------------------------
st.subheader("3. Add a Task")

col1, col2 = st.columns(2)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
    duration   = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col2:
    priority  = st.selectbox("Priority", ["high", "medium", "low"])
    task_time = st.text_input("Start time (HH:MM, optional)", value="", placeholder="e.g. 08:00")
    frequency = st.selectbox("Frequency", ["daily", "weekly", "monthly", "as needed"])

if st.button("Add task", type="primary"):
    # Basic time format guard
    time_val = task_time.strip()
    if time_val and (len(time_val) != 5 or time_val[2] != ":"):
        st.warning("Start time must be in HH:MM format (e.g. 08:00) or left blank.")
    else:
        new_task = Task(
            title=task_title.strip(),
            duration=int(duration),
            priority=priority,
            pet=pet,
            time=time_val,
            frequency=frequency,
            due_date=date.today(),
        )
        owner.schedule.add_task(new_task)
        st.success(f"Task **{task_title}** added ({priority} priority).")

st.divider()

# ---------------------------------------------------------------------------
# Section 4: Task List (sorted + conflict warnings)
# ---------------------------------------------------------------------------
st.subheader("4. Current Tasks")

if not owner.schedule.tasks:
    st.info("No tasks yet — add one above.")
else:
    # --- Conflict warnings (persistent, always visible) ---
    conflicts = owner.schedule.get_conflicts()
    if conflicts:
        for time_slot, clashing_tasks in conflicts.items():
            task_names = " and ".join(
                f"**{t.title}** ({t.pet.name})" for t in clashing_tasks
            )
            st.warning(
                f"**Scheduling conflict at {time_slot}** — {task_names} are both "
                f"scheduled at the same time. Edit one task's start time to resolve."
            )

    # --- Sort / filter controls ---
    col_a, col_b = st.columns(2)
    with col_a:
        sort_by = st.radio("Sort by", ["Time", "Priority"], horizontal=True)
    with col_b:
        status_filter = st.radio("Show", ["Pending", "Completed", "All"], horizontal=True)

    status_key = status_filter.lower()  # matches "pending" / "completed" / "all"

    if sort_by == "Time":
        tasks_to_show = owner.schedule.get_schedule_by_time(status=status_key)
    else:
        tasks_to_show = owner.schedule.get_schedule(status=status_key)

    if not tasks_to_show:
        st.info(f"No {status_filter.lower()} tasks.")
    else:
        PRIORITY_COLOR = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        rows = []
        for t in tasks_to_show:
            badge = PRIORITY_COLOR.get(t.priority, "⚪")
            rows.append({
                "Priority":  f"{badge} {t.priority.capitalize()}",
                "Task":      t.title,
                "Time":      t.time if t.time else "—",
                "Duration":  f"{t.duration} min",
                "Frequency": t.frequency,
                "Done":      "✅" if t.completed else "",
            })
        st.table(rows)

    # --- Mark complete ---
    pending_tasks = owner.schedule.get_schedule(status="pending")
    if pending_tasks:
        st.markdown("**Mark a task complete:**")
        task_to_complete = st.selectbox(
            "Select task",
            pending_tasks,
            format_func=lambda t: f"{t.title} ({t.priority})",
            label_visibility="collapsed",
        )
        if st.button("Mark complete"):
            owner.schedule.complete_task(task_to_complete)
            freq = task_to_complete.frequency
            if freq in ("daily", "weekly"):
                st.success(
                    f"**{task_to_complete.title}** marked done. "
                    f"Next {freq} occurrence scheduled automatically."
                )
            else:
                st.success(f"**{task_to_complete.title}** marked done.")
            st.rerun()

st.divider()

# ---------------------------------------------------------------------------
# Section 5: Generate Daily Plan
# ---------------------------------------------------------------------------
st.subheader("5. Generate Daily Plan")
available_minutes = st.number_input(
    "How many minutes do you have today?",
    min_value=10, max_value=480, value=60,
)

if st.button("Generate plan", type="primary"):
    plan = owner.schedule.get_daily_plan(available_minutes=int(available_minutes))

    if not plan:
        st.warning(
            "No tasks fit within your available time. "
            "Try increasing available minutes or reducing task durations."
        )
    else:
        total = sum(t.duration for t in plan)
        st.success(
            f"Scheduled **{len(plan)} task(s)** using **{total} of {int(available_minutes)} min**."
        )

        PRIORITY_COLOR = {"high": "🔴", "medium": "🟡", "low": "🟢"}
        for i, t in enumerate(plan, 1):
            badge = PRIORITY_COLOR.get(t.priority, "⚪")
            with st.container(border=True):
                cols = st.columns([0.08, 0.6, 0.32])
                cols[0].markdown(f"**{i}.**")
                cols[1].markdown(
                    f"{badge} **{t.title}**"
                    + (f"  ·  {t.time}" if t.time else "")
                )
                cols[2].markdown(f"`{t.duration} min` · {t.priority}")

        # Flag any conflicts in the plan
        plan_times = [t.time for t in plan if t.time]
        if len(plan_times) != len(set(plan_times)):
            st.warning(
                "Your plan contains tasks at the same start time. "
                "Resolve conflicts in the task list above."
            )
