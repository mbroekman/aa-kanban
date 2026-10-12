---
id: TASK-61
title: Move ticket board config to board settings
status: Done
assignee:
  - '@antigravity'
created_date: '2026-09-29 06:54'
updated_date: '2026-09-29 06:57'
labels: []
dependencies: []
type: feature
ordinal: 77000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Move ticket board configuration from global settings to a checkbox (is_ticket_board) per board in board settings.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->
- [x] #1 Board model has is_ticket_board boolean
- [x] #2 Create and edit board forms include checkbox
- [x] #3 Board overview displays badge for ticket boards
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added is_ticket_board boolean field, updated views/forms, and added badge in index view.
<!-- SECTION:NOTES:END -->
