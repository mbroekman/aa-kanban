---
id: TASK-1.2
title: Datamodellen implementeren en unit tests schrijven
status: Done
assignee:
  - '@antigravity'
created_date: '2026-09-09 20:10'
updated_date: '2026-09-09 20:30'
labels: []
dependencies:
  - TASK-1.1
parent_task_id: TASK-1
priority: high
type: feature
ordinal: 3000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implementatie van Board (met read_groups en write_groups AA Group koppeling), List, Card, Label, Comment in models.py met juiste relaties, constraints, ordering en unit tests.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Board model met naam, slug, beschrijving, groups (AA Group M2M) en timestamps
- [x] #2 List model met board FK, naam, order integer en ordering
- [x] #3 Card model met list FK, titel, beschrijving, order integer, assignees M2M en timestamps
- [x] #4 Label en Comment modellen voor tags en reacties
- [x] #5 Django migratie gegenereerd zonder fouten
- [x] #6 Pytest fixtures en unittests dekken alle modellen en validaties af
- [x] #7 Admin registraties toegevoegd in admin.py
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Definieer modellen in aa_kanban/models.py: General, Board (met view_groups en write_groups), List, Card, Label, Comment
2. Voeg custom QuerySets/Managers en can_user_view/can_user_write methoden toe
3. Genereer Django migratie voor aa_kanban
4. Registreer modellen in aa_kanban/admin.py met filter_horizontal en list_display
5. Schrijf uitgebreide pytest fixtures en model tests in aa_kanban/tests/test_models.py
6. Draai pytest en ruff check
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Datamodellen geïmplementeerd in aa_kanban/models.py (Board met view_groups en write_groups, List, Card, Label, Comment). Migratie 0001_initial gegenereerd. Admin configuratie ingericht in admin.py. 10 unittests geschreven en geslaagd in test_models.py. Ruff en Mypy checks 100% succesvol.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Datamodellen, migraties, admin classes en model tests succesvol geïmplementeerd en geverifieerd via pytest en mypy.
<!-- SECTION:FINAL_SUMMARY:END -->
