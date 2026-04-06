# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**
Three core actions that the user should be able to perform:
1. Add a pet care task. ex: medicine to be fed at between 8 AM to 10 AM .
2. Add constraints. ex: need to head to work at 9AM.
3. User adds a pet. ex: support for more than one pet, cat dog etc.
4. User is able to see all tasks for the day.


- Briefly describe your initial UML design.

Four classes: Owner has a collection of Pets (composition pets don't exist without an owner). Task holds a duration, priority, title, and a reference to the Pet it's assigned to. Schedule ties everything together, it belongs to one Owner and holds a list of Tasks, with methods to add tasks and retrieve the full schedule.



- What classes did you include, and what responsibilities did you assign to each?

Basically: an owner has pets, tasks are assigned to individual pets, and a schedule aggregates those tasks under an owner.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, claude chat identified some bottlenecks and I kept the following:

Added a back-reference from Pet to Owner (defaulting to None) that gets set automatically when add_pet is called, keeping the link in sync without extra manual wiring. Moved Schedule creation into Owner.__init__ so the two are always paired — callers access it via owner.schedule instead of instantiating it separately. Added a guard in Schedule.add_task that raises a ValueError if the task's pet isn't in the owner's pet list, preventing orphaned tasks from being silently added to the wrong schedule.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers three constraints: **available time** (the owner's daily minute budget), **priority** (high / medium / low, mapped to a numeric sort key), and **start time** (an optional HH:MM string used for chronological ordering and conflict detection). Priority was treated as the most important constraint because a pet owner's first instinct when time is tight is to protect the most critical tasks — medications and feeding — not optimize the clock. Available minutes came second because it's the hard outer limit. Start time was treated as a soft preference rather than a rigid requirement, which is why tasks without a time are accepted and simply sorted last.

**b. Tradeoffs**

**Exact start-time matching instead of duration overlap detection**

The scheduler's `get_conflicts()` method flags two tasks as conflicting only when their `time` strings are identical (e.g., both set to `"08:00"`). It does not check whether the *duration* of one task overlaps with the start of another. For example, a 30-minute walk starting at `"08:00"` and a 10-minute feeding starting at `"08:20"` actually overlap in real time, but the scheduler does not catch this because their start times differ.

This is a deliberate simplification. Implementing true duration-overlap detection would require converting `time` strings to `datetime` objects, adding the `duration` as a `timedelta`, and checking whether any two intervals intersect — roughly four times more code for a feature that matters most in tightly packed schedules. For a pet care app where tasks are spaced across a full day (morning feeding, midday walk, evening grooming), exact-time matching catches the most common mistake — accidentally double-booking the same slot — without the added complexity.

The tradeoff is reasonable for this scenario because pet care schedules are loosely packed by nature. If the app were scheduling back-to-back appointments in a veterinary clinic, duration-overlap detection would be the right choice.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

Claude (via Claude Code) was the primary AI tool throughout the project. It was used across every phase: design brainstorming (generating a first-pass UML and identifying missing back-references), implementation (writing and iterating on `Schedule` methods), test generation (drafting the full pytest suite against the test plan), UI upgrades (replacing raw `st.table` output with sorted, conflict-aware Streamlit components), and documentation (the README feature table and this reflection).

The most effective prompts were **context-heavy and specific**: rather than asking "write a test for the scheduler," the most useful sessions provided the full class signatures and asked for tests targeting named edge cases — like "confirm that completing a daily task with no due_date falls back to date.today() without crashing." Claude also responded well to prompts framed around **intent rather than implementation** ("the conflict warning should be persistent and actionable for a non-technical pet owner") — that framing produced better UI decisions than asking for specific Streamlit calls.

Which Copilot/Claude features were most effective:
- **Inline code generation with full context** — reading the existing file before suggesting changes meant Claude never introduced mismatched signatures or missed imports.
- **Test plan generation** — asking Claude to reason about edge cases from the class structure (before writing any test code) produced a more complete coverage map than writing tests directly would have.
- **Iterative refinement in chat** — being able to say "the warning should name the tasks, not just the time slot" and get an immediate targeted revision saved significant back-and-forth.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

Early in the project, Claude suggested implementing duration-overlap detection in `get_conflicts()` — converting `time` strings to `datetime` objects, computing end times via `timedelta`, and checking interval intersections. The suggestion was technically correct but added roughly four times more code for a benefit that doesn't matter in a loosely-packed pet care schedule. I rejected it and kept exact start-time matching, documenting the deliberate tradeoff in this reflection and in a code comment. The evaluation process was straightforward: I asked whether the added complexity would change outcomes for a realistic day's worth of pet tasks (morning feeding, midday walk, evening grooming) — and the answer was no. A veterinary clinic with back-to-back appointments would need interval detection; a home pet schedule does not. Verifying the simpler version was easy because the behavior could be tested with a single assertion: two tasks at different start times produce no conflict, even if their durations overlap.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

The suite covers four areas across 16 tests: **sorting correctness** (chronological order, timeless tasks pushed last, priority tie-breaking by title), **recurrence logic** (daily +1 day, weekly +7 days, non-recurring frequencies skipped, missing `due_date` fallback to today, full property inheritance), **conflict detection** (same-slot flagging, no false positives on different times, tasks without time ignored, warnings formatted correctly, `ValueError` on unowned pet), and **core task behavior** (completion flag, pet task list count).

These tests mattered because the three scheduling features — sorting, recurrence, and conflict detection — are invisible to the user unless they fail visibly (wrong order, missed follow-up, silent duplicate booking). Unit tests make those failures deterministic and reproducible rather than discovered during a demo.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

**4 out of 5.** The tested behaviors are reliable. The missing star is the known gap: duration-overlap conflicts are undetected by design. Additional tests I would add with more time:
- `get_daily_plan()` with a single task larger than the budget (should be excluded)
- completing a task whose `frequency` is `"monthly"` (should not reschedule)
- an owner with two pets where `get_tasks_for_pet()` correctly isolates each
- `explain_plan()` output format when the plan is empty vs. populated
- adding the same task object twice (currently allowed — should it deduplicate?)

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The part I'm most satisfied with is the conflict detection and its UI presentation. The technical implementation is intentionally simple (exact start-time matching), but the Streamlit layer makes it genuinely useful: warnings are persistent rather than transient, they name the specific tasks involved, and they include a one-line resolution hint. That combination — a deliberate simplification in the backend paired with clear communication in the UI — is a pattern I'd carry into future projects. It also reflects a real design principle: the right level of complexity depends on who is affected by the failure, not just what's technically possible.

How separate chat sessions helped with organization: keeping each phase in its own session (design → logic → tests → UI → documentation) meant each conversation had a narrow, well-defined goal. There was no risk of an earlier context ("add a back-reference to Pet") leaking into a later session ("generate test cases") and producing suggestions aimed at the wrong version of the code. It also made it easier to reject or roll back a phase's work without losing progress in other areas — each session was a clean commit boundary in both git and in thinking.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would redesign the `Schedule` class to support multiple pets more naturally. Currently `get_tasks_for_pet()` filters after the fact, but the schedule is effectively a flat list. A better structure would be a `dict[Pet, list[Task]]` internally, making per-pet retrieval O(1) and making it impossible to accidentally add a task for Pet A to Pet B's view. I would also replace the `time: str` field on `Task` with a proper `datetime.time` object — this would unlock true duration-overlap detection and make the sort logic cleaner (no string comparison, no `"99:99"` sentinel hack).

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The most important lesson was that **AI makes you a faster architect, not a less necessary one**. Claude could generate a working scheduler, a full test suite, and a polished UI in minutes — but every one of those outputs required a human decision about what to keep, what to simplify, and what to reject. The duration-overlap tradeoff, the choice to keep `time` as a string, the decision to make conflict warnings persistent instead of transient — none of those were in Claude's prompts. They came from understanding the actual user (a pet owner, not a clinic scheduler) and the actual constraints (a student project with a clear scope). AI tools compress the gap between an idea and a working implementation, but they can't tell you which idea is the right one. That judgment — knowing when "good enough" is correct and when simplification becomes a bug — is what it means to be the lead architect.

---

*Reflection completed: April 2026*
