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

Gebruiker wil dat men bij het aanmaken van een ticket alleen nog een Team hoeft te selecteren. Op basis van dat team wordt het bijbehorende board bepaald. We moeten een `ticket_board` (ForeignKey naar Board) toevoegen aan `KanbanTeam`. In het `create_ticket` formulier verwijderen we de 'board' select, en de POST logica haalt het board uit het gekozen team.

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->

- [x] #1 KanbanTeam heeft een ForeignKey naar Board
- [x] #2 Het create_ticket formulier toont alleen een Team dropdown, geen Board dropdown
- [x] #3 Nieuwe tickets worden automatisch in het board van het geselecteerde team geplaatst

<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->

1. Add ticket_board FK to KanbanTeam. 2. Make/apply migrations. 3. Update team create/edit forms/views to include ticket_board. 4. Update create_ticket_form.html to remove board dropdown. 5. Update create_ticket view to derive board from team.

<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->

Added ticket_board ForeignKey to KanbanTeam and generated migration 0016. Updated create_kanban_team and edit_kanban_team views and forms to handle ticket_board. Removed board dropdown from ticket_form.html and made team dropdown required. Updated create_ticket view to infer the target board from the chosen team.

<!-- SECTION:NOTES:END -->
