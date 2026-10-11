---
id: TASK-73
title: Notify Discord thread on card move, label, or team change
status: Done
assignee:
  - '@antigravity'
created_date: '2026-10-09 21:20'
updated_date: '2026-10-09 21:23'
labels:
  - feature
  - discord
  - tickets
dependencies: []
ordinal: 89000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

Wanneer een ticket card gekoppeld is aan een Discord thread (`discord_thread_id`), moeten wijzigingen direct in de thread worden gemeld:

1. Wanneer de kaart naar een andere kolom/lijst wordt verplaatst (bijv. van 'Backlog' naar 'In Progress').
1. Wanneer het toegewezen team verandert (of ontkoppeld wordt), inclusief eventuele role mention en auto-invite van nieuwe teamleden.
1. Wanneer labels worden toegevoegd of verwijderd van de kaart.

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->

- [x] #1 Celery task `notify_ticket_thread` en async bot helper geïmplementeerd om berichten in een Discord thread te plaatsen
- [x] #2 Bij verplaatsen van een card (`move_card` en `services.move_kanban_card`) wordt een statusupdate in de thread gepost
- [x] #3 Bij wijzigen van team (`update_card_team`) wordt een teamupdate in de thread gepost (met auto-invite van nieuwe teamleden naar de thread)
- [x] #4 Bij toevoegen of verwijderen van een label (`toggle_label`) wordt een labelupdate in de thread gepost
- [x] #5 Unit tests geschreven en geslaagd

<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->

1. Voeg `_send_discord_thread_message` async runner en `notify_ticket_thread` Celery task toe aan `tasks.py`.
1. Werk `views_api.py` bij in `move_card`, `update_card_team`, en `toggle_label` om `notify_ticket_thread.delay(...)` aan te roepen indien `card.discord_thread_id` aanwezig is.
1. Werk `services.py` bij in `move_kanban_card`.
1. Voeg vertalingen (NL en EN) toe voor de notificatieberichten.
1. Schrijf unit tests in `aa_kanban/tests/` om alle scenario's te verifiëren.

<!-- SECTION:PLAN:END -->
