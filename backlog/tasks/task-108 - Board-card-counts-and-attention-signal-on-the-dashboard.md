---
id: TASK-108
title: Board card counts and attention signal on the dashboard
status: Done
assignee: []
created_date: '2026-11-05 08:50'
updated_date: '2026-11-05 09:04'
labels:
  - feature
dependencies: []
ordinal: 122000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The board overview shows per board how many open cards it holds and flags boards with cards that need attention: overdue (due date passed), inactive past the board's stale_card_alert_hours, or a column over its WIP limit. Cards in the last list or a done-named list count as finished and never need attention.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Each board card shows the number of open (non-archived) cards
- [x] #2 A board with overdue cards, inactive cards or a column over its WIP limit shows an attention badge with the counts per reason
- [x] #3 Finished cards (last list or done-named list) and archived cards never count as needing attention
- [x] #4 The counts use a fixed number of queries, not one per board
- [x] #5 Tests cover the counts, each reason and the dashboard render
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
New aa_kanban/board_stats.py: two queries for all boards (lists, then non-archived cards with last comment). Finished = last list or a done-named list (same keywords as stale alerts). Inactive uses the board's stale_card_alert_hours, so boards with stale alerts off never flag inactivity. NL translations added by hand (no gettext on devauth); .mo built with polib.

Deployed to devauth (committed code only; the uncommitted services/tasks/views_api work was not synced). Dashboard renders 200; counts: Indy Tracker 10, Kanban development 11, Ticket Tracking 0; no board needs attention there.
<!-- SECTION:NOTES:END -->
