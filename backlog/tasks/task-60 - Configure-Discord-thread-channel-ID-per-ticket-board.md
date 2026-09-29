---
id: TASK-60
title: Configure Discord thread channel ID per ticket board
status: Done
assignee:
  - '@antigravity'
created_date: '2026-09-29 06:47'
updated_date: '2026-09-29 06:49'
labels: []
dependencies: []
type: feature
ordinal: 76000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
De gebruiker wil per ticket board een Discord channel ID kunnen opgeven voor het aanmaken van ticket threads, in plaats van één globale instelling in KanbanSettings. We moeten een `ticket_channel_id` of vergelijkbaar toevoegen aan het `Board` model, of deze verplaatsen van de global settings naar de boards.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Het `Board` model heeft een veld voor Discord kanaal ID
- [x] #2 Bij het aanmaken van een ticket wordt de thread gemaakt in het kanaal van het specifieke board
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add discord_ticket_channel_id to Board model. 2. Create Django migration. 3. Update forms to allow setting this on the board (create_board_form.html, edit_board_form.html). 4. Remove ticket_channel_id from KanbanSetting? Or leave it as a fallback? Let's check how it's used. 5. Update tasks.py where the thread is created to use the board's channel ID.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added discord_ticket_channel_id to Board model. Created migration. Updated create_board and edit_board views and forms to handle the new field. Updated create_ticket_thread task to use the board's specific ticket channel if set, otherwise falling back to the global setting.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Implemented Discord thread channel ID configuration per ticket board, allowing flexible ticket setups instead of relying strictly on the global setting.
<!-- SECTION:FINAL_SUMMARY:END -->
