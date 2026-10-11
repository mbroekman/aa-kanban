---
id: TASK-78
title: Fix hardcoded Dutch strings in stale card alerts (i18n & Celery translation)
status: Done
assignee: []
created_date: '2026-10-11 21:04'
updated_date: '2026-10-11 21:10'
labels: []
dependencies: []
ordinal: 94000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
De meldingen van kaarten die te lang stilstaan (stale card alerts) worden verzonden in het Nederlands in plaats van het Engels wanneer Engels de ingestelde taal is. Zorg dat de meldingsteksten standaard in het Engels zijn (conform AA standaard) en vertaald worden via gettext/i18n of expliciet de geconfigureerde taal respecteren.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Stale card alert teksten in tasks.py zijn standaard in het Engels
- [x] #2 Vertaalbare strings met gettext / lazy translation correct afgehandeld in Celery task
- [x] #3 Unit tests verifieren Engelse output van stale card alerts
<!-- AC:END -->
