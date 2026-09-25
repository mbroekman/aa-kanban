---
id: TASK-26
title: Fix WIP limit update visibility
status: Done
assignee: []
created_date: '2026-09-25 20:53'
updated_date: '2026-09-25 20:54'
labels: []
dependencies: []
ordinal: 34000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
When updating the WIP limit of a list, the UI is not updating without a refresh. Need to return an OOB swap for the column header when saving list settings.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 WIP limit is immediately visible after saving
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Kanban.js was overwriting the WIP limit display when updateListCounts() was called after the HTMX swap. Modified updateListCounts() in kanban.js to read the wip limit from the column header dataset and render the badge appropriately with X/Y format and proper color coding.
<!-- SECTION:NOTES:END -->
