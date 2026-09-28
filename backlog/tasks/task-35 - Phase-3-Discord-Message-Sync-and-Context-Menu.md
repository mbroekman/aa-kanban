---
id: TASK-35
title: 'Phase 3: Discord Message Sync and Context Menu'
status: Done
assignee: []
created_date: '2026-09-27 18:28'
updated_date: '2026-09-27 18:29'
labels: []
dependencies: []
ordinal: 43000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

Create an aadiscordbot Cog for aa-kanban that listens for messages in ticket threads to sync back as comments. Add a Discord message context menu command to upload specific messages to a ticket.

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->

- [ ] #1 Messages in a ticket thread are saved as Card Comments in aa_kanban, users can right click a message in discord and upload it as a comment

<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->

Created aa_kanban/cogs.py with KanbanTicketCog. Listens to on_message to sync messages from ticket threads back to Kanban Card comments. Added Upload to Ticket app_command context menu. Registered the cog in auth_hooks.py.

<!-- SECTION:NOTES:END -->
