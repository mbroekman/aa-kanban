---
id: TASK-1.5
title: HTMX en SortableJS Drag & Drop integratie
status: Done
assignee:
  - '@antigravity'
created_date: '2026-09-09 20:10'
updated_date: '2026-09-09 21:18'
labels: []
dependencies:
  - TASK-1.4
parent_task_id: TASK-1
priority: medium
type: feature
ordinal: 6000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Drag & drop van kaarten tussen kolommen en herschikken binnen kolommen via SortableJS en HTMX backend updates.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 SortableJS initialiseert op kolom containers
- [x] #2 Kaarten kunnen tussen kolommen en binnen kolommen worden versleept
- [x] #3 Backend endpoint /cards/<id>/move/ verwerkt updates atomair (transaction.atomic)
- [x] #4 HTMX verwerkt asynchrone updates zonder page reload
- [x] #5 Foutafhandeling bij netwerkfouten of ontbrekende permissies
- [x] #6 Tests voor card move API
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Download en vendor HTMX (v1.9.12) en SortableJS (v1.15.2) in aa_kanban/static/aa_kanban/libs/
2. Implementeer move_card endpoint in views_api.py met @login_required, basic_access permissie en board write verificatie via transaction.atomic()
3. Ondersteun atomic reordering binnen dezelfde kolom en verplaatsing tussen kolommen van hetzelfde bord, inclusief herindexering
4. Schrijf frontend JavaScript in aa_kanban/static/aa_kanban/js/kanban.js voor SortableJS initialisatie op .kanban-cards containers, drag & drop event handling en foutafhandeling
5. Integreer scripts en styling in board_detail.html
6. Schrijf uitgebreide tests in aa_kanban/tests/test_api.py (binnen lijst, tussen lijsten, cross-board blokkade, permissies, 403 checks)
7. Valideer met pytest, ruff en mypy
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
SortableJS en HTMX assets geïnstalleerd. Endpoint /cards/<id>/move/ verwerkt kaartverschuivingen atomair in transaction.atomic(), inclusief herindexering en cross-board validatie. Drag & drop styling en JS met automatische revert en Bootstrap 5 toast error handling geïmplementeerd. 9 API tests toegevoegd en 100% test passing.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Geïmplementeerd: Drag & drop functionaliteit met SortableJS en HTMX, inclusief backend endpoint, atomische herordening, permissiebeveiliging en foutafhandeling. 34 tests slagen foutloos.
<!-- SECTION:FINAL_SUMMARY:END -->
