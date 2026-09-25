---
id: TASK-22
title: Fix HTMX form reset
status: Done
assignee: []
created_date: '2026-09-25 12:58'
updated_date: '2026-09-25 13:20'
labels: []
dependencies: []
ordinal: 30000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Fix hx-on attribute syntax so forms reset after submission.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Forms clear after successful submission
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Removed all hx-on attributes from templates to prevent CSP violations in Alliance Auth. Replaced with a global event listener in kanban.js.
<!-- SECTION:NOTES:END -->
