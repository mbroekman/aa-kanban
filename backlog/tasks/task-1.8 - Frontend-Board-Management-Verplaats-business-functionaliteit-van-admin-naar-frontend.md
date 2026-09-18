---
id: TASK-1.8
title: >-
  Frontend Board Management - Verplaats business-functionaliteit van admin naar
  frontend
status: Done
assignee: []
created_date: '2026-09-10 06:47'
updated_date: '2026-09-10 06:53'
labels: []
dependencies: []
parent_task_id: TASK-1
priority: high
type: feature
ordinal: 9000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Alle business-functionaliteit (aanmaken/bewerken/verwijderen van boards, lists, cards) verplaatsen van Django admin naar de frontend. Admin wordt readonly voor business-entities. Permissie manage_boards bewaakt board-aanmaak. Group-selectie via <select multiple>.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Gebruiker met manage_boards kan board aanmaken via frontend modal zonder admin te bezoeken
- [ ] #2 Gebruiker met write-rechten kan lists (kolommen) aanmaken, hernoemen en verwijderen inline via HTMX
- [ ] #3 Gebruiker met write-rechten kan cards aanmaken inline per kolom via HTMX
- [ ] #4 Board bewerken (naam, beschrijving, view/write groups via select multiple) beschikbaar via frontend
- [ ] #5 Board verwijderen via frontend met bevestigingsdialoog
- [ ] #6 Admin toont BoardAdmin/ListAdmin/CardAdmin/LabelAdmin als read-only (geen add/change)
- [ ] #7 pytest volledige suite slaagt incl. nieuwe test_board_management.py
- [ ] #8 ruff check en mypy passeren zonder fouten
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Alle business-functionaliteit verplaatst van admin naar frontend. Geïmplementeerd: create_board, edit_board, delete_board (views.py), create_list, rename_list, delete_list, create_card (views_api.py). Admin is readonly voor Board/List/Card/Label. Nieuwe templates: index.html (Nieuw bord knop), board_detail.html (inline kolom- en kaartbeheer, rename via klik, delete, board-settings modal). Partials: create_board_form.html, edit_board_form.html, board_column.html, column_header.html, card_item.html. Tests: test_board_management.py (23 tests). Verificatie: 69/69 pytest, ruff OK, mypy OK (20 source files).
<!-- SECTION:NOTES:END -->
