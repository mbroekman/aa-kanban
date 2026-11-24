---
id: TASK-120
title: Fix drag-and-drop on iPad / touch devices in SPA board
status: In Progress
assignee: []
created_date: '2026-11-24 19:20'
updated_date: '2026-11-24 19:20'
labels: []
dependencies: []
priority: medium
type: bug
ordinal: 134000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Kaarten slepen werkt niet op een iPad. Oorzaak: `BoardView.tsx` gebruikt alleen een `PointerSensor` met `distance: 6`. Op iPadOS Safari neemt de browser de touch over om te scrollen en vuurt `pointercancel` af voordat de drag activeert. Oplossing: `MouseSensor` (desktop ongewijzigd) + `TouchSensor` met long-press (`delay: 200, tolerance: 8`), plus `touch-action: manipulation` en `-webkit-touch-callout: none` op de kaarten.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Board gebruikt MouseSensor + TouchSensor i.p.v. alleen PointerSensor
- [x] #2 SPA-bundle opnieuw gebouwd (`aa_kanban/static/aa_kanban/spa/assets/`)
- [ ] #3 Live geverifieerd op een iPad (long-press en slepen verplaatst kaart, swipe scrollt nog)
<!-- AC:END -->
