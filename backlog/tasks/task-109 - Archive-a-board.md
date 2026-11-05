---
id: TASK-109
title: Archive a board
status: In Progress
assignee: []
created_date: '2026-11-05 09:51'
labels:
  - feature
dependencies: []
ordinal: 123000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Board managers (and the board's creator) can archive a board. An archived board disappears from the dashboards, the summary and the ticket form, is read-only for everyone, gets no stale alerts, intake API cards or Discord comments, and can be opened read-only and restored by board managers from an Archived Boards page.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Archive Board in the board settings modal and Restore on the board and on the Archived Boards page, both behind the app's confirm modal
- [ ] #2 An archived board is hidden from the dashboard, members page, summary and ticket form
- [ ] #3 An archived board is read-only for everyone and only board managers and its creator can open it
- [ ] #4 No stale alerts, intake API cards or Discord thread comments on an archived board
- [ ] #5 Tests cover archive, restore, visibility and read-only
<!-- AC:END -->
