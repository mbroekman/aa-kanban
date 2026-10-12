---
id: TASK-2
title: 'Bug: Adding a board results in an infinite spinning icon'
status: Done
assignee: []
created_date: '2026-09-21 06:59'
updated_date: '2026-10-12 07:13'
labels: []
dependencies: []
type: bug
ordinal: 10000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
When a user tries to create a new board, an infinite spinning loading icon is displayed. Caused by missing HTMX script loading.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Board can be successfully added via UI
- [x] #2 No infinite spinning loading icon on success or validation failure
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Root cause: htmx.min.js was not loaded on index.html, causing the hx-get on the 'New Board' button to be ignored. Resolved by including htmx.min.js centrally in base.html in extra_javascript block.
<!-- SECTION:NOTES:END -->
