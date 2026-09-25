---
id: TASK-19
title: Custom Menu Name
status: Done
assignee: []
created_date: '2026-09-25 12:41'
updated_date: '2026-09-25 12:42'
labels: []
dependencies: []
ordinal: 27000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Make the kanban menu text configurable via Django settings (AA_KANBAN_APP_NAME).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Menu name defaults to Kanban, but can be overridden in local.py
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Updated auth_hooks.py to use getattr(settings, 'AA_KANBAN_APP_NAME', 'Kanban') and added documentation to README.md
<!-- SECTION:NOTES:END -->
