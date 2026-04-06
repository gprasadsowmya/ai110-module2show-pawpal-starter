---
name: logic_layer_agent
description: This agent will flesh out the logic layer for pawpal.
tools: Read, Grep, Glob, Bash # specify the tools this agent can use. If not set, all enabled tools are allowed.
---

<!-- Tip: Use /create-agent in chat to generate content with agent assistance -->

Define what this custom agent does, including its behavior, capabilities, and any specific instructions for its operation.


Flesh out the logic layer for the classes in pawpal_system.py.

Task: Represents a single activity (description, time, frequency, completion status).


Pet: Stores pet details and a list of tasks.


Owner: Manages multiple pets and provides access to all their tasks.


Scheduler: The "Brain" that retrieves, organizes, and manages tasks across pets.