---
id: TASK-11
title: Fix missing description column error
status: Done
assignee: []
created_date: '2026-09-22 11:41'
updated_date: '2026-09-22 11:41'
labels: []
dependencies: []
ordinal: 19000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
User gets OperationalError: Unknown column 'aa_kanban_list.description' in 'SELECT' when opening a board. The migration needs to be applied to the development database.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Migration is applied; Board opens without OperationalError
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Ran `python manage.py migrate` to apply the aa_kanban.0004_list_description_list_wip_limit migration on the local dev database.
<!-- SECTION:NOTES:END -->
