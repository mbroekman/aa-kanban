---
id: TASK-1.1
title: Set up test harness and development environment
status: Done
assignee:
  - '@antigravity'
created_date: '2026-09-09 20:10'
updated_date: '2026-09-09 20:25'
labels: []
dependencies:
  - TASK-1.7
parent_task_id: TASK-1
priority: high
type: task
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Set up testauth and pytest configuration so that pytest-django and unit tests run cleanly locally.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->
- [x] #1 testauth configuration configured for pytest
- [x] #2 pytest runs cleanly via pytest runner
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Configured testauth layout with testauth/settings/local.py (bound to PACKAGE = 'aa_kanban'), urls.py, and SQLite test database. Added pytest-django, pytest-cov, and factory_boy. Added smoke tests in aa_kanban/tests/test_smoke.py. Verification passed with 100% clean ruff check.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Testauth test harness and pytest environment successfully set up.
<!-- SECTION:FINAL_SUMMARY:END -->
