---
id: TASK-10
title: Create release for Kanban Group Member update
status: Done
assignee: []
created_date: '2026-09-22 11:34'
updated_date: '2026-09-22 11:36'
labels: []
dependencies: []
ordinal: 18000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Commit open changes and create a new GitHub release.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Changes are committed; version bumped; new GitHub release created
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Created git commit for open changes. Bumped version to 0.6.0 in aa_kanban/__init__.py and updated CHANGELOG.md. Tagged and pushed to remote, and created GitHub release v0.6.0 using gh CLI.
<!-- SECTION:NOTES:END -->
