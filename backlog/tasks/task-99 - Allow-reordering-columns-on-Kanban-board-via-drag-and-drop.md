---
id: TASK-99
title: Allow reordering columns on Kanban board via drag-and-drop
status: Done
assignee: []
created_date: '2026-10-14 10:39'
updated_date: '2026-10-14 10:39'
labels: []
dependencies: []
priority: medium
type: feature
ordinal: 113000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Enable users to reorder lists/columns within a Kanban board via drag-and-drop, persisting position updates to the backend.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 SortableJS initialized on board container for columns with header handle and grip icon
- [x] #2 Atomic reorder service function `reorder_kanban_list` and API endpoint `move_list`
- [x] #3 Position updates persist across page reloads and clamp safely within board bounds
- [x] #4 Comprehensive unit tests cover permission checks, reordering, out-of-bound clamping, and JSON payloads
- [x] #5 Live verification on devauth sandbox succeeded
<!-- AC:END -->
