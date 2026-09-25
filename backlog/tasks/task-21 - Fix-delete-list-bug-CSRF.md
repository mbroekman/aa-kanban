---
id: TASK-21
title: Fix delete list bug & CSRF
status: Done
assignee: []
created_date: '2026-09-25 12:55'
updated_date: '2026-09-25 12:55'
labels: []
dependencies: []
ordinal: 29000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Fix broken list deletion for newly created columns and add global HTMX CSRF handler.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Newly added columns can be deleted, global CSRF token is sent with hx-post
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Fixed board_column.html delete button and added global HTMX CSRF hook in base.html.
<!-- SECTION:NOTES:END -->
