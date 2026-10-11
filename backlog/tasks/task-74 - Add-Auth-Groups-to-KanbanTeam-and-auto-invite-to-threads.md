---
id: TASK-74
title: Add Auth Groups to KanbanTeam and auto-invite to Discord threads
status: Done
assignee:
  - '@antigravity'
created_date: '2026-10-09 21:30'
updated_date: '2026-10-09 21:40'
labels:
  - feature
  - discord
  - teams
dependencies: []
ordinal: 90000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

Teams (`KanbanTeam`) kunnen momenteel alleen individuele gebruikers gekoppeld krijgen. Breid `KanbanTeam` uit met een ManyToMany relatie naar Django `Group` (Auth Groups), zodat complete groepen aan een team gekoppeld kunnen worden via de frontend settings UI. Zorg dat bij de automatische Discord thread auto-invite (zowel bij het aanmaken van een ticket als bij teamtoewijzing) alle leden van zowel de directe teamleden als de gekoppelde auth groepen worden uitgenodigd.

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->

- [x] #1 `KanbanTeam` model uitgebreid met `groups = ManyToManyField(Group)` en migratie aangemaakt
- [x] #2 Frontend settings UI uitgebreid zodat Auth Groups geselecteerd en beheerd kunnen worden voor een `KanbanTeam`
- [x] #3 Auto-invite in `tasks.py` verzamelt zowel directe teamleden als leden via gekoppelde auth groepen
- [x] #4 Unit tests geschreven en geslaagd

<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->

1. Voeg `groups = models.ManyToManyField(Group, blank=True, related_name="kanban_ticket_teams")` toe aan `KanbanTeam` in `models.py`.
1. Maak migratie `0020_kanbanteam_groups.py` aan.
1. Werk `views_settings.py`, `urls.py` en `team_users_modal.html` bij met endpoints voor toevoegen/verwijderen van auth groups aan teams.
1. Werk `tasks.py` bij in `_create_discord_thread` en `_send_discord_thread_message` om alle users (direct + via groups) op te halen.
1. Schrijf unit tests en valideer via remote test suite.

<!-- SECTION:PLAN:END -->
