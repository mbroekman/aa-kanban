---
id: TASK-36
title: Ticket Submission Permission
status: Done
assignee: []
created_date: '2026-09-27 19:20'
updated_date: '2026-09-27 19:22'
labels: []
dependencies: []
ordinal: 44000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

Add create_ticket permission and separate menu item for it

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->

- [ ] #1 create_ticket permission exists, separate menu item for Submit Ticket is shown if user has create_ticket perm, view is protected by create_ticket perm

<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->

Added create_ticket permission to General model. Added AaKanbanCreateTicketMenuItem to auth_hooks.py to render 'Submit Ticket' in the menu if the user has the permission. Protected create_ticket and ticket_success views with the new permission.

<!-- SECTION:NOTES:END -->
