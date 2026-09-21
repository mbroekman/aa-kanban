---
id: TASK-3
title: Frontend Settings voor Groepsbeheer
status: Done
assignee: []
created_date: '2026-09-21 08:32'
updated_date: '2026-09-21 08:42'
labels: []
dependencies: []
ordinal: 11000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Een settings pagina in de Kanban frontend waar gebruikers groepen kunnen aanmaken en beheren, inclusief het toewijzen van gebruikers aan deze groepen, zodat dit niet (alleen) via de Django admin hoeft.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Er is een Settings knop/pagina in de Kanban frontend.
Gebruikers met manage_boards permissie kunnen hier nieuwe groepen aanmaken.
Gebruikers kunnen aan deze groepen worden toegevoegd of verwijderd vanuit deze settings pagina.
Deze groepen kunnen vervolgens aan borden worden gekoppeld (view/write).

- [ ] #2 1
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented custom KanbanGroup model, replacing Django Group. Updated Board model and all permission logic to use KanbanGroup. Created Settings UI using HTMX for managing KanbanGroups and assigning users. Refactored 69 tests to use KanbanGroup and pass.
<!-- SECTION:NOTES:END -->
