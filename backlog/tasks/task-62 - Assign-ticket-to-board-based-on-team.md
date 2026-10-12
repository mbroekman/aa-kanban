---
id: TASK-62
title: Assign ticket to board based on team
status: Done
assignee:
  - '@antigravity'
created_date: '2026-09-29 07:06'
updated_date: '2026-09-29 07:25'
labels: []
dependencies: []
type: feature
ordinal: 78000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Allow users to select only a Team when creating a ticket, deriving the destination board automatically from the team's linked ticket_board.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->
- [x] #1 KanbanTeam has a ticket_board ForeignKey to Board
- [x] #2 create_ticket form displays only Team dropdown without redundant board select
- [x] #3 New tickets are automatically placed in the team's linked board
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added ticket_board FK to KanbanTeam, updated forms and views to infer board from selected team.
<!-- SECTION:NOTES:END -->
