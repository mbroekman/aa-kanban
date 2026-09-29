---
id: TASK-66
title: >-
  Fix bug: ticket creation does not result in a card on the board or thread in
  Discord
status: Done
assignee: []
created_date: '2026-09-29 13:29'
updated_date: '2026-09-29 13:35'
labels: []
dependencies: []
ordinal: 82000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
User reports that submitting a ticket results in neither a card on the board nor a thread in the Discord channel. Investigating views.py and tasks.py.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Ticket is created properly and visible on board.,Discord thread is created or error is caught gracefully.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Fixed Discord thread creation failing silently due to channel cache miss by using fetch_channel fallback. Fixed card placement using case-insensitive column name matching.
<!-- SECTION:NOTES:END -->
