---
id: TASK-15
title: Show description tooltip on name hover
status: Done
assignee: []
created_date: '2026-09-22 12:50'
updated_date: '2026-09-22 12:50'
labels: []
dependencies: []
ordinal: 23000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Added tooltips containing the description to both the list (column) name and the card title to improve UX when hovering over records.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Hovering over list name shows list description; Hovering over card title shows card description; Tooltips initialize correctly after HTMX swaps.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added data-bs-toggle='tooltip' with title=description to column_header.html (List name) and card_item.html (Card title). Also updated kanban.js to re-init tooltips on htmx:afterSwap so dynamic loads maintain tooltips.
<!-- SECTION:NOTES:END -->
