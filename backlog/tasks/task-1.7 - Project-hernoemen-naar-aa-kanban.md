---
id: TASK-1.7
title: Project hernoemen naar aa-kanban
status: Done
assignee:
  - '@antigravity'
created_date: '2026-09-09 20:15'
updated_date: '2026-09-09 20:17'
labels: []
dependencies: []
parent_task_id: TASK-1
priority: high
type: task
ordinal: 8000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Volledige hernoeming van het project, Python package, templates, auth_hooks en configuraties van aa_trello/aa-trello naar aa_kanban/aa-kanban.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Python package hernoemd van aa_trello naar aa_kanban
- [x] #2 pyproject.toml, Makefile, tox.ini en configs bijgewerkt naar aa-kanban
- [x] #3 Templates en static mappen hernoemd naar aa_kanban
- [x] #4 Editable installatie in .venv bijgewerkt en import aa_kanban geslaagd
- [x] #5 Ruff check slaagt zonder fouten
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Hernoem aa_trello/ naar aa_kanban/ via git mv
2. Hernoem template mappen aa_kanban/templates/aa_trello naar aa_kanban/templates/aa_kanban
3. Update pyproject.toml (name, keywords, build includes, version path)
4. Update aa_kanban/apps.py, auth_hooks.py, views.py, urls.py en README.md
5. Update Makefile, tox.ini en pytest.ini voor aa_kanban
6. Herinstalleer editable in .venv (pip install -e .) en test import aa_kanban
7. Voer ruff check uit
<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Package directory aa_trello hernoemd naar aa_kanban via git mv. Alle configuraties (pyproject.toml, Makefile, tox.ini, README.md), code (apps.py, auth_hooks.py, views.py, urls.py, models.py, admin.py) en templates bijgewerkt naar aa_kanban. Editable installatie uitgevoerd en import geverifieerd. Ruff checks 100% geslaagd.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Project en Python package succesvol hernoemd naar aa_kanban. Import en ruff controles geverifieerd.
<!-- SECTION:FINAL_SUMMARY:END -->
