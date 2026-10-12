---
id: TASK-85
title: Release v0.13.0
status: Done
assignee: []
created_date: '2026-10-12 15:23'
updated_date: '2026-10-12 16:44'
labels: []
dependencies: []
ordinal: 99000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Minor release bundling TASK-77 (Markdown + image support in card/ticket descriptions), TASK-78/79 (i18n + patch release, already in 0.12.1), TASK-80/81 (already in 0.12.1), TASK-82 (description field contrast fix), TASK-83 (card modal spinner hang fix), and TASK-84 (frontend-managed can_manage_boards flag on KanbanGroup). Version bumped 0.12.1 -> 0.13.0, CHANGELOG finalized, README and User Manual updated.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 aa_kanban/__init__.py version bumped to 0.13.0
- [ ] #2 CHANGELOG.md Unreleased section finalized as [0.13.0] - 2026-10-12
- [ ] #3 README.md and backlog/docs/doc-4 User Manual updated for image/markdown support and can_manage_boards
- [ ] #4 Git tag v0.13.0 created and pushed
- [ ] #5 GitHub Release published
- [ ] #6 Package published to PyPI
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Release published: GitHub release v0.13.0 (https://github.com/mbroekman/aa-kanban/releases/tag/v0.13.0), PyPI publish workflow succeeded, aa-kanban 0.13.0 confirmed live on PyPI. gh CLI installed via winget and authenticated via device flow (user completed browser confirmation) to enable this; git http.sslBackend set to schannel locally to fix a pre-existing TLS verification issue blocking push (Git's bundled OpenSSL CA bundle vs. Windows cert store).
<!-- SECTION:NOTES:END -->
