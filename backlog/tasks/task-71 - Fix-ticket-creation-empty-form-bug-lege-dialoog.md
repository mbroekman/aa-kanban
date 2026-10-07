---
id: TASK-71
title: Fix ticket creation empty form bug (lege dialoog)
status: Done
assignee: []
created_date: '2026-10-02 15:09'
updated_date: '2026-10-02 15:10'
labels: []
dependencies: []
ordinal: 87000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Users were getting an empty form (lege dialoog) when creating a ticket because they selected a team without a ticket board. Fixed by filtering the team dropdown and preserving form inputs on validation error.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Dropdown only shows valid teams, Form preserves user input on validation failure
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Filtered teams dropdown to only show teams with a valid ticket board. Added value='...' attributes to ticket form inputs so they are preserved on validation errors.
<!-- SECTION:NOTES:END -->
