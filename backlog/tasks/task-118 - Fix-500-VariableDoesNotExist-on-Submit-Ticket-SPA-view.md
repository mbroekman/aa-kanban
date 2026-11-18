---
id: TASK-118
title: Fix 500 VariableDoesNotExist on Submit Ticket SPA view
status: Done
assignee: []
created_date: '2026-11-18 13:55'
updated_date: '2026-11-18 13:56'
labels: []
dependencies: []
ordinal: 132000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Include app_name and title in create_ticket context and guard spa.html page_title against missing title/app_name.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 GET /kanban/tickets/create/ returns 200 with SPA mount point
- [x] #2 Test added in test_spa_api.py and passes
<!-- AC:END -->
