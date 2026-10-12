---
id: TASK-1.8
title: Frontend Board Management - Move business functionality from admin to frontend
status: Done
assignee: []
created_date: '2026-09-10 06:47'
updated_date: '2026-09-10 06:53'
labels: []
dependencies: []
parent_task_id: TASK-1
priority: high
type: feature
ordinal: 9000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Move board creation, editing, and list management from Django admin to the frontend UI.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->
- [x] #1 Create and edit board forms available in frontend
- [x] #2 Manage lists and WIP limits directly in frontend
- [x] #3 Restricted to users with manage_boards permission
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added frontend modals and views for creating boards, editing boards, and managing lists without requiring Django admin access.
<!-- SECTION:NOTES:END -->
