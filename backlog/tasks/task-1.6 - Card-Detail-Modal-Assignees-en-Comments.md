---
id: TASK-1.6
title: 'Card Detail Modal, Assignees en Comments'
status: Done
assignee:
  - '@antigravity'
created_date: '2026-09-09 20:10'
updated_date: '2026-09-09 22:03'
labels: []
dependencies:
  - TASK-1.5
parent_task_id: TASK-1
priority: low
type: feature
ordinal: 7000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Bootstrap 5 modal geladen via HTMX voor het bekijken en bewerken van kaarten (titel, beschrijving, toewijzen gebruikers, reacties).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Klikken op kaart opent Bootstrap 5 modal dynamisch via HTMX
- [ ] #2 Modal toont details, assignees en comments
- [ ] #3 Inline bewerken of toevoegen van assignees en comments via HTMX
- [ ] #4 Tests voor card modal en interactie endpoints
- [ ] #5 #1,#2,#3,#4
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Implementeer views_api.card_modal view die een Bootstrap 5 modal HTML partial rendert met kaartdetails, labels, assignees en comments.
2. Bouw template partial aa_kanban/partials/card_modal_content.html met Bootstrap 5 modal-header, modal-body en modal-footer.
3. Ondersteun permission gating: can_write bepaalt of commentaren toegevoegd kunnen worden, beschrijving gewijzigd kan worden en assignees gekoppeld kunnen worden.
4. Implementeer views_api.add_comment endpoint (POST /cards/<id>/comments/add/) die direct de bijgewerkte commentarenlijst als HTMX partial teruggeeft.
5. Implementeer views_api.toggle_assignee endpoint (POST /cards/<id>/assignees/toggle/) om gebruikers toe te wijzen of te verwijderen.
6. Werk board_detail.html bij zodat hx-get point naar {% url 'aa_kanban:card_modal' card.id %}.
7. Schrijf uitgebreide tests in aa_kanban/tests/test_modal.py (modal rendering, comments toevoegen, assignees togglen, permissiebeveiliging).
8. Valideer met pytest, ruff en mypy.
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
De functionaliteit voor de Card Detail Modal was al grotendeels geïmplementeerd. De comment author werd echter incorrect aangesproken in de card_comments.html partial (created_by in plaats van author), wat resulteerde in een falende test in test_modal.py. Dit is gecorrigeerd. Daarnaast zijn mypy errors in views_api.py verholpen en is de test_modal.py geformatteerd met ruff. pytest, ruff en mypy passeren nu succesvol.
<!-- SECTION:NOTES:END -->
