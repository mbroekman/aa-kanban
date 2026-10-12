---
id: TASK-76
title: Recreate release v0.12.0
status: Done
assignee: []
created_date: '2026-10-11 16:12'
updated_date: '2026-10-12 07:12'
labels: []
dependencies: []
ordinal: 92000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Commit uv.lock, move git tag v0.12.0 to HEAD (including CI fixes), republish GitHub Release, and verify pre-commit/automated checks on GitHub.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 uv.lock committed and pushed
- [x] #2 Tag v0.12.0 points to latest HEAD on origin
- [x] #3 GitHub Release v0.12.0 published
- [x] #4 Automated checks workflow green on GitHub
<!-- AC:END -->
