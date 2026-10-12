---
id: TASK-59
title: Summary view missing columns from multiple boards
status: Done
assignee:
  - '@antigravity'
created_date: '2026-09-29 06:36'
updated_date: '2026-09-29 06:37'
labels: []
dependencies: []
type: bug
ordinal: 75000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The summary view previously displayed columns from only the first board. Fixed to render columns and cards dynamically per board.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->
- [x] #1 Summary view renders correct lists/columns for each visible board
- [x] #2 Cards are properly grouped in their respective columns across all boards
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Updated summary.html to dynamically loop over board.lists.all and calculate grid-template-columns per board.
<!-- SECTION:NOTES:END -->
