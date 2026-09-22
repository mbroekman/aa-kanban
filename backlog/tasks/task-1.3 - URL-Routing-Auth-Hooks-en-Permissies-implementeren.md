---
id: TASK-1.3
title: 'URL Routing, Auth Hooks en Permissies implementeren'
status: Done
assignee:
  - '@antigravity'
created_date: '2026-09-09 20:10'
updated_date: '2026-09-09 20:33'
labels: []
dependencies:
  - TASK-1.2
parent_task_id: TASK-1
priority: medium
type: feature
ordinal: 4000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Inrichten van toegangscontrole (AA Group checks), navigatiemenu in auth_hooks.py en URL routing.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 auth_hooks.py registreert menu item met passend icoon en URL hook
- [x] #2 General permissies basic_access en manage_boards gedefinieerd
- [x] #3 Toegangsbescherming voor boards gebaseerd op AA User groepen
- [x] #4 Tests voor toegangscontrole en permissies
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Maak permissie helpers en decorators in aa_kanban/permissions.py voor object-level toegangscontrole (board view en board write)
2. Werk auth_hooks.py bij met nette documentatie en controle op basic_access
3. Richt urls.py in met routes voor board overzicht en board detail
4. Schrijf tests in aa_kanban/tests/test_auth_hooks.py en test_permissions.py
5. Valideer met pytest, ruff en mypy
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Inrichting van auth_hooks.py (AaKanbanMenuItem met basic_access check en UrlHook ^kanban/). Permissie helpers en decorators gebouwd in aa_kanban/permissions.py (board_view_required en board_write_required). URLs geconfigureerd in aa_kanban/urls.py. Unittests geschreven in test_auth_hooks.py en test_permissions.py. Ruff, Mypy en Pytest 100% geslaagd.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Auth hooks, URL routing en permissie-decorators voor readonly en write toegangscontrole succesvol geïmplementeerd en getest.
<!-- SECTION:FINAL_SUMMARY:END -->
