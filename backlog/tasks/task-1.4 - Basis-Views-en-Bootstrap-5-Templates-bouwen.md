---
id: TASK-1.4
title: Basis Views en Bootstrap 5 Templates bouwen
status: Done
assignee:
  - '@antigravity'
created_date: '2026-09-09 20:10'
updated_date: '2026-09-09 20:38'
labels: []
dependencies:
  - TASK-1.3
parent_task_id: TASK-1
priority: medium
type: feature
ordinal: 5000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Views en Bootstrap 5 templates voor boardoverzicht en board detail (kolommen met kaarten).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Board overzichtspagina toont alleen borden waar de ingelogde gebruiker toegang toe heeft
- [x] #2 Board detailpagina toont bord, kolommen en kaarten in Kanban layout
- [x] #3 Bootstrap 5 styling met data-bs-* syntax conform AA v5
- [x] #4 Zero N+1 queries met prefetch_related op kolommen en kaarten
- [x] #5 Tests voor board overzicht en detail views
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Verfijn views.py voor index (board list) en board_detail met geoptimaliseerde prefetch_related queries (lists, cards, labels, assignees)
2. Bouw Bootstrap 5 templates: index.html (bord cards, status badges, overzicht) en board_detail.html (Kanban bord met kolommen, cards, badges, assignees)
3. Zorg voor data-bs-* attributes en strakke Bootstrap 5 styling
4. Schrijf view tests in aa_kanban/tests/test_views.py (inclusief permissiecontroles, context checks en query count controles)
5. Valideer met pytest, ruff en mypy
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Views en Bootstrap 5 templates gebouwd voor index (board overview) en board_detail (Kanban columns & cards). Prefetching op lists, cards, assignees en labels zorgt voor zero N+1 queries. Bootstrap 5 markup conform AA v5 en 100% test passing in test_views.py.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Geïmplementeerd: index en board_detail views en templates conform AA v5 en Bootstrap 5 richtlijnen. Tests, ruff en mypy slagen foutloos.
<!-- SECTION:FINAL_SUMMARY:END -->
