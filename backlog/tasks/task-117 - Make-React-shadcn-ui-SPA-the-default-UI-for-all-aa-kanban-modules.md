---
id: TASK-117
title: Make React + shadcn/ui SPA the default UI for all aa-kanban modules
status: Done
assignee: []
created_date: '2026-11-18 12:40'
updated_date: '2026-11-18 12:46'
labels: []
dependencies: []
ordinal: 131000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Expand the React/shadcn SPA and JSON API to cover all aa-kanban features (board CRUD/archive/restore, column edit/delete/reorder, archived cards, summary view, ticket submission, global search, and settings for groups, teams, labels, and global config) and make the SPA the default UI across aa-kanban routes.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 JSON API covers boards CRUD/archive/restore, columns edit/delete, archived cards, summary, ticket creation, and settings (groups, teams, labels, global)
- [x] #2 SPA implements all views with adaptive light/dark shadcn/ui
- [x] #3 Default aa-kanban routes serve the SPA while preserving classic fallback or updating tests cleanly
- [x] #4 Vite build, ruff check/format, and pytest pass
<!-- AC:END -->
