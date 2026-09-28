---
id: TASK-51.1
title: 'Datamodellen: Board, List, Card, Assignees'
status: To Do
assignee: []
created_date: '2026-09-28 19:14'
labels: []
dependencies: []
parent_task_id: TASK-51
ordinal: 60000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

Implement Django models for the Kanban app. The application requires at least: Board, List, Card, Card Assignees. Create the `models.py` file and write pytest fixtures and tests directly.

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->

- [ ] #1 Board model has name, description, and m2m to Group for access control
- [ ] #2 List model has name, order, and FK to Board
- [ ] #3 Card model has title, description, creation date, order, and FK to List
- [ ] #4 Users can be assigned to Cards (m2m)
- [ ] #5 Pytest tests cover model creation and relations

<!-- AC:END -->
