---
id: TASK-34
title: 'Phase 2: Discord Ticket Thread Creation'
status: Done
assignee: []
created_date: '2026-09-27 18:06'
updated_date: '2026-09-27 18:15'
labels: []
dependencies: []
ordinal: 42000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

Implement Celery task and Discord bot logic to create a Discord thread when a new ticket is submitted. Ping the reporter and the assigned team role.

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->

- [ ] #1 Submitting a ticket creates a thread via aadiscordbot, the thread mentions the reporter, the thread mentions the assigned team, the card saves the discord_thread_id

<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->

Added ticket_channel_id to KanbanSettings. Created Celery task in tasks.py using aadiscordbot run_task_function to asynchronously spawn a thread and save discord_thread_id to the Card.

<!-- SECTION:NOTES:END -->
