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
Verplaats de configuratie om een board in te stellen als ticket board van de globale KanbanSettings (via een select) naar een simpele checkbox (is_ticket_board) per board in de instellingen (aanmaken/bewerken). Verwijder de ticket_boards M2M relatie uit KanbanSetting. Voeg ook een badge/tag toe in het board overzicht (index) om aan te geven of een board een ticket board is.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Board model heeft is_ticket_board boolean
- [x] #2 KanbanSetting.ticket_boards is verwijderd of uitgefaseerd
- [x] #3 Create/edit forms voor boards bevatten de checkbox
- [x] #4 In het board overzicht (index.html) staat een badge/tag bij ticket boards
- [x] #5 Aanmaken van tickets haalt ticket boards op via Board.objects.filter(is_ticket_board=True)
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add is_ticket_board to Board model and remove ticket_boards from KanbanSetting. 2. Update views.py (create_board, edit_board) to handle is_ticket_board checkbox and update create_ticket view. 3. Update forms (create_board_form.html, edit_board_form.html). 4. Update index.html to show badge. 5. Remove ticket_boards from settings.html. 6. Make and apply migrations.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added is_ticket_board checkbox on the board create/edit forms. Removed the old ticket_boards selector from KanbanSetting globally. Adjusted create_ticket to query Boards for ticket_board status. Added a badge to the index page to mark ticket boards.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Successfully moved the ticket board assignment from global settings to the board level itself, simplifying the config flow.
<!-- SECTION:FINAL_SUMMARY:END -->
