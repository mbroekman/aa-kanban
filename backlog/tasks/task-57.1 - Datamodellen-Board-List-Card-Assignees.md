---
id: TASK-57.1
title: 'Datamodellen (Board, List, Card, Assignees)'
status: Done
assignee:
  - '@antigravity'
created_date: '2026-09-29 06:15'
updated_date: '2026-09-29 06:19'
labels: []
dependencies: []
parent_task_id: TASK-57
ordinal: 70000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

Genereer models.py met Board, List, Card, en Card Assignees. Inclusief pytest fixtures en tests.

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->

- [x] #1 Board model aanwezig met Group relatie
- [x] #2 List model aanwezig met foreign key naar Board
- [x] #3 Card model aanwezig met foreign key naar List
- [x] #4 Assignees relatie tussen Card en AA User
- [x] #5 Pytest fixtures en unit tests aanwezig voor alle modellen

<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->

1. Create models.py with Board, List, Card, and Card Assignees models. 2. Implement the foreign keys and m2m relationships correctly. 3. Setup tests in pytest for these models.

<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->

The datamodels were already mostly present but some tests in test_models.py were failing because Label doesn't take a board argument. Fixed the tests so they all pass.

<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

Fixed failing test suite for datamodels. Verified all tests pass with pytest.

<!-- SECTION:FINAL_SUMMARY:END -->
