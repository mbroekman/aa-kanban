---
id: TASK-28
title: Fix card modal close on delete
status: Done
assignee: []
created_date: '2026-09-25 21:10'
updated_date: '2026-09-25 21:10'
labels: []
dependencies: []
ordinal: 36000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The closeModal HTMX trigger in kanban.js only closes listModal, not cardModal. Need to add logic to close cardModal so it dismisses when a card is deleted.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Card modal automatically closes after deletion
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Updated kanban.js to hide cardModal as well as listModal when the closeModal HTMX event is triggered.
<!-- SECTION:NOTES:END -->
