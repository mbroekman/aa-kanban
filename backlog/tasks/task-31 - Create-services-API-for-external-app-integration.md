---
id: TASK-31
title: Create services API for external app integration
status: Done
assignee: []
created_date: '2026-09-26 17:19'
updated_date: '2026-09-26 17:19'
labels: []
dependencies: []
ordinal: 39000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement a `services.py` module to act as the official Python API for external plugins (like aa-industry) to safely interact with Kanban boards and cards without bypassing core business logic like webhooks.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 services.py exists with create_card, create_board functions, Webhooks are properly triggered in the service methods
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Created aa_kanban/services.py with create_kanban_board, create_kanban_card, and move_kanban_card functions. These functions encapsulate object creation and trigger webhook notifications when appropriate, ensuring external plugins can safely interact with Kanban without bypassing business logic.
<!-- SECTION:NOTES:END -->
