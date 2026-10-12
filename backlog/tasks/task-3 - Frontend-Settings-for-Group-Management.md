---
id: TASK-3
title: Frontend Settings for Group Management
status: Done
assignee: []
created_date: '2026-09-21 08:32'
updated_date: '2026-10-12 07:13'
labels: []
dependencies: []
ordinal: 11000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A settings page in the Kanban frontend where users can create and manage groups, including assigning users to these groups, without requiring Django admin access.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Settings page accessible in Kanban frontend for users with manage_boards permission

- [x] #2 Create, update, and delete groups in frontend settings
- [x] #3 Add and remove users to groups in frontend settings
- [x] #4 Link groups to boards for view and write access
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented custom KanbanGroup model, replacing Django Group. Updated Board model and all permission logic to use KanbanGroup. Created Settings UI using HTMX for managing KanbanGroups and assigning users. Refactored 69 tests to use KanbanGroup and pass.
<!-- SECTION:NOTES:END -->
