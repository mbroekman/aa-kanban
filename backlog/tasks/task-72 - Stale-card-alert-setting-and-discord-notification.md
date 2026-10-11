---
id: TASK-72
title: Stale card alert setting and Discord notification
status: Done
assignee:
  - '@antigravity'
created_date: '2026-10-09 21:05'
updated_date: '2026-10-09 21:13'
labels:
  - feature
  - discord
dependencies: []
ordinal: 88000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

Voeg een instelling toe aan een Board (`stale_card_alert_hours`) waarmee gesignaleerd kan worden wanneer kaarten te lang stilstaan (gemeten in uren). Wanneer kaarten de drempelwaarde overschrijden, wordt er elk uur een gebundelde melding op het geconfigureerde Discord kanaal (via bot of webhook) geplaatst met een overzicht van de kaarten die stilstaan, inclusief kolom, stilstandduur en toewijzingen. Kolommen met 'Done' of 'Afgerond' worden automatisch uitgesloten van de signalering.

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->

- [x] #1 Veld `stale_card_alert_hours` (PositiveIntegerField, default 0) en Discord alert configuratie toegevoegd aan `Board` model
- [x] #2 Migratie aangemaakt en toegepast
- [x] #3 Board create en edit formulieren en templates bijgewerkt met velden voor de stale card drempelwaarde en Discord alert instellingen
- [x] #4 Celery periodic task `check_stale_cards` geïmplementeerd die elk uur draait
- [x] #5 Stale cards detectie berekent inactiviteit (rekening houdend met updates en comments) en sluit 'Done'/'Afgerond' kolommen uit
- [x] #6 Discord melding verzendt een geformatteerd overzicht naar het Discord kanaal (via aadiscordbot channel ID of webhook)
- [x] #7 Unit tests geschreven en geslaagd

<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->

1. Breid `Board` model uit met `stale_card_alert_hours`, `discord_alert_channel_id` en `discord_alert_webhook`.
1. Genereer en documenteer Django migratie.
1. Werk `views.py` en HTML templates (`create_board_form.html`, `edit_board_form.html`) bij inclusief i18n vertalingen.
1. Implementeer de Celery periodic task `check_stale_cards` en helper in `tasks.py` met Discord bot/webhook dispatch.
1. Registreer periodic task in Celery beat configuratie.
1. Schrijf tests in `aa_kanban/tests/` om de logica te valideren.

<!-- SECTION:PLAN:END -->
