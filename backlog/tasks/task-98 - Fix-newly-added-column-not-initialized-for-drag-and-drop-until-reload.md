---
id: TASK-98
title: Fix newly added column not initialized for drag-and-drop until reload
status: Done
assignee: []
created_date: '2026-10-14 09:05'
labels: []
dependencies: []
priority: high
type: bug
ordinal: 112000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
When a new column is added to a Kanban board via HTMX, cards cannot be dragged into it until the user reloads or navigates back. This occurs because SortableJS is only initialized on initial page load and not re-initialized or bound to newly appended columns.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 SortableJS initializes on dynamically added .kanban-cards containers
- [x] #2 Moving cards into a newly added column works immediately without reloading
- [x] #3 Column addition HTMX event triggers sortable initialization
- [x] #4 All tests pass on devauth sandbox
<!-- AC:END -->
