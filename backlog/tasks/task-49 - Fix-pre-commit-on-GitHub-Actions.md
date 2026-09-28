---
id: TASK-49
title: Fix pre-commit on GitHub Actions
status: Done
assignee: []
created_date: '2026-09-28 18:56'
updated_date: '2026-09-28 18:58'
labels: []
dependencies: []
ordinal: 57000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Explicitly provide config paths for ESLint and Stylelint to fix CI failures.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 args added, pushed, github action passes
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Explicitly defined config file locations for ESLint and Stylelint via --config argument to bypass GitHub Actions runner path resolution issues.
<!-- SECTION:NOTES:END -->
