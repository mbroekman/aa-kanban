---
id: TASK-8
title: Add KanbanGroup rename and member overview
status: Done
assignee: []
created_date: '2026-09-22 11:14'
updated_date: '2026-09-22 11:15'
labels: []
dependencies: []
ordinal: 16000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement a rename functionality for Kanban groups and ensure members overview is clearly accessible in the settings page.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 - [x] Group name can be edited/renamed in settings
- [x] Group member overview is clear and accessible
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented an HTMX view/modal to edit/rename Kanban groups, and added a direct display of the first 5 members as badges in the settings table for immediate overview. Deleting members was already possible via the manage users modal.
<!-- SECTION:NOTES:END -->
