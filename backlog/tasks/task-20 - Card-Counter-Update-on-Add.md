---
id: TASK-20
title: Card Counter Update on Add
status: Done
assignee: []
created_date: '2026-09-25 12:46'
updated_date: '2026-09-25 12:46'
labels: []
dependencies: []
ordinal: 28000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Fix issue where adding a card via HTMX does not update the column counter badge and leaves the empty placeholder visible.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Counter updates instantly when card added, empty placeholder hides instantly
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Updated kanban.js to hook into htmx:afterSwap to automatically update the counter badge and hide the empty placeholder when a card is added or removed.
<!-- SECTION:NOTES:END -->
