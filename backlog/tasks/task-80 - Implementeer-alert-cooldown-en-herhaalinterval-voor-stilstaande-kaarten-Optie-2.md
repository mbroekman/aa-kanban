---
id: TASK-80
title: >-
  Implementeer alert cooldown en herhaalinterval voor stilstaande kaarten (Optie
  2)
status: Done
assignee: []
created_date: '2026-10-12 06:56'
updated_date: '2026-10-12 07:02'
labels: []
dependencies: []
ordinal: 96000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Voorkom uurlikse alert-spam voor kaarten die stilstaan door het toevoegen van last_stale_alert_at op Card en stale_card_repeat_hours op Board (default 24 uur, 0 = eenmalig). Kaarten worden pas opnieuw gealerteerd nadat het herhaalinterval is verstreken.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Veld stale_card_repeat_hours toegevoegd aan Board model en formulieren
- [x] #2 Veld last_stale_alert_at toegevoegd aan Card model
- [x] #3 Django database migratie gegenereerd en toegepast
- [x] #4 get_stale_cards() respecteert cooldown en herhaalinterval
- [x] #5 check_stale_cards() taak werkt last_stale_alert_at bij na verzending
- [x] #6 Unit tests verifieren throttling, herhaling en eenmalig melden (0 uur)
<!-- AC:END -->
