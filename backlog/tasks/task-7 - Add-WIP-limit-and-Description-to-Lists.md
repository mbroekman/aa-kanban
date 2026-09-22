---
id: TASK-7
title: Add WIP limit and Description to Lists
status: Done
assignee: []
created_date: '2026-09-22 10:40'
updated_date: '2026-09-22 10:50'
labels: []
dependencies: []
ordinal: 15000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement a modal to edit column name, WIP limits, and descriptions. Backend should enforce WIP limits.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 - List has wip_limit and description fields;- edit_list_modal.html created;- Settings gear opens modal;- Backend enforces WIP limit;- Description shown as tooltip/info icon
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented WIP limits and descriptions for Kanban columns. Created edit modal, updated drag-and-drop JS for WIP restrictions, and enforced limits server-side.
<!-- SECTION:NOTES:END -->
