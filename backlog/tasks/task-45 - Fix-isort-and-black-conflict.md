---
id: TASK-45
title: Fix isort and black conflict
status: To Do
assignee: []
created_date: '2026-09-28 18:07'
labels: []
dependencies: []
ordinal: 53000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
isort and black are constantly formatting files in a loop. Add profile='black' to isort config.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 conflict resolved, pre-commit passes
<!-- AC:END -->
