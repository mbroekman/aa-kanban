---
id: TASK-18
title: Multiple Ticket Boards
status: Done
assignee: []
created_date: '2026-09-25 12:34'
updated_date: '2026-09-25 12:37'
labels: []
dependencies: []
ordinal: 26000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Allow the KanbanSettings to configure multiple ticket boards (ManyToManyField) and update the ticket submission form to let users choose the destination board.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 KanbanSetting uses ManyToManyField for ticket_boards, Settings UI supports selecting multiple boards, create_ticket view shows a dropdown of available ticket boards, Discord notifications trigger correctly
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Migrated KanbanSetting.ticket_board to ticket_boards (ManyToManyField). Updated views and templates to allow administrators to select multiple ticket boards in the settings panel. Users now select the target board (Department) when submitting a ticket.
<!-- SECTION:NOTES:END -->
