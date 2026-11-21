---
name: audit-handoffs
description: Audit completion claims and identify the next authorized step from a project queue without taking over a live assignment.
---

# Audit handoffs

Compare the queue, project handoff and actual evidence. Confirm that a completed claim points to the same artifact or code revision that was tested. Record pass, revise or blocked with the file or verification result that drove the conclusion.

For queued work, verify authorization, the current task, the live agent's state and the most recent receipt before redispatching. Treat sending, receiving and finishing as separate events. Keep one active assignment per lead. When human input is pending, record the blocker. Leave publishing, merging to a protected branch and permission changes to an authorized owner.

Use read-only inspection by default. If the owner sets up scheduled auditing, give the job a run budget and a fixed queue source. Report new discrepancies and actionable blockers rather than heartbeat messages.
