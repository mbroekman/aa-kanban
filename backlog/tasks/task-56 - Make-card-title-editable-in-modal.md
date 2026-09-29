---
id: TASK-56
title: Make card title editable in modal
status: Done
assignee: []
created_date: '2026-09-28 21:37'
updated_date: '2026-09-28 22:41'
labels: []
dependencies: []
ordinal: 68000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

Allow users with write access to change the title of a card directly from the card modal. Updating the title must also reflect on the kanban board.

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->

- [ ] #1 Card title can be edited in the modal
- [ ] #2 Updating the title updates the card on the board via HTMX OOB
- [ ] #3 1
- [ ] #4 2

<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->

Made modal title an inline HTMX form that updates title and syncs to board via OOB.

<!-- SECTION:NOTES:END -->
