---
id: TASK-51
title: Develop native Kanban (Trello-like) App
status: Done
assignee: []
created_date: '2026-09-28 19:14'
updated_date: '2026-09-29 06:22'
labels: []
dependencies: []
ordinal: 59000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

Develop a custom Django app for Alliance Auth (AA) called `aa-kanban`. This app provides full Kanban functionality within the AA environment, similar to Trello. Code must strictly follow Alliance Auth developer guidelines and .cursorrules.

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->

- [ ] #1 Boards can be created and linked to specific Alliance Auth Groups
- [ ] #2 Lists can be added to Boards with an order
- [ ] #3 Cards can be added to Lists with a title, description, creation date, and order
- [ ] #4 Alliance Auth Users can be assigned to Cards
- [ ] #5 UI uses standard Alliance Auth Bootstrap 3/5 themes
- [ ] #6 HTMX and SortableJS are used for drag-and-drop between lists without page reload
- [ ] #7 Permissions use @permission_required decorators
- [ ] #8 App is integrated into AA menu via auth_hooks.py

<!-- AC:END -->
