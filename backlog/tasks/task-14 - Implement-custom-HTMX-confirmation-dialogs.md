---
id: TASK-14
title: Implement custom HTMX confirmation dialogs
status: Done
assignee: []
created_date: '2026-09-22 12:42'
updated_date: '2026-09-22 12:43'
labels: []
dependencies: []
ordinal: 22000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Replace all native browser hx-confirm dialogs with a global Bootstrap 5 modal by intercepting htmx:confirm in base.html.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Native browser prompts no longer appear; Bootstrap modal appears instead; Confirm and Cancel actions work correctly
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Injected custom htmxConfirmModal inside aa_kanban/templates/aa_kanban/base.html and added JS listener for htmx:confirm event to intercept all native hx-confirm prompts globally across the application.
<!-- SECTION:NOTES:END -->
