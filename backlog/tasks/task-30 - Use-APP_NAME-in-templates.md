---
id: TASK-30
title: Use APP_NAME in templates
status: Done
assignee: []
created_date: '2026-09-26 16:20'
updated_date: '2026-09-26 16:22'
labels: []
dependencies: []
ordinal: 38000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
User requested that the Kanban dashboard label matches the menu label, which is controlled by the AA_KANBAN_APP_NAME setting.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 index.html uses app_name context variable, board_detail uses app_name
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Injected the AA_KANBAN_APP_NAME setting as an app_name context variable in the views, and updated the templates (index, board_detail, summary, and settings) to dynamically render this name in headers and titles instead of a hardcoded 'Kanban'.
<!-- SECTION:NOTES:END -->
