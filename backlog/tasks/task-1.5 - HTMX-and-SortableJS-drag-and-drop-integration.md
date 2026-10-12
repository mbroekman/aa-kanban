---
id: TASK-1.5
title: HTMX and SortableJS drag-and-drop integration
status: Done
assignee:
  - '@antigravity'
created_date: '2026-09-09 20:10'
updated_date: '2026-09-09 21:18'
labels: []
dependencies:
  - TASK-1.4
parent_task_id: TASK-1
priority: medium
type: feature
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Integrate HTMX and SortableJS for smooth drag-and-drop reordering of cards within and between lists.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->
- [x] #1 SortableJS enables dragging cards across columns
- [x] #2 HTMX asynchronously updates card list and position in backend
- [x] #3 Backend validates move permissions and saves new order
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Integrated SortableJS on column card containers with HTMX post endpoint to persist ordering.
<!-- SECTION:NOTES:END -->
