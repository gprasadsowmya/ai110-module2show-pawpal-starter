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

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
