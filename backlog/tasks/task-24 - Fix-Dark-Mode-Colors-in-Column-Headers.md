---
id: TASK-24
title: Fix Dark Mode Colors in Column Headers
status: Done
assignee: []
created_date: '2026-09-25 18:04'
updated_date: '2026-09-25 18:05'
labels: []
dependencies: []
ordinal: 32000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
In the dark theme, the card count badge and the edit icon in the column headers have the same color as the background, making them invisible or hard to see. Needs to be contrasted appropriately for readability.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Card count badge is visible in dark theme\nEdit icon is visible in dark theme
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added custom CSS targeting the count badge and the edit button in .kanban-column .card-header to use translucent grey backgrounds and inherit color. This ensures they always contrast perfectly with the header background in both light and dark modes.
<!-- SECTION:NOTES:END -->
