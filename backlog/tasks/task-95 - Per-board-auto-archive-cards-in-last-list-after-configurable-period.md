---
id: TASK-95
title: Per-board auto-archive cards in last list after configurable period
status: Done
assignee: []
created_date: '2026-10-13 16:13'
updated_date: '2026-10-13 16:30'
labels: []
dependencies: []
ordinal: 109000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Keep boards clean: per board, configure a number of days a card may sit in the LAST list before being automatically archived. Archived cards disappear from the normal board view and are only reachable via a new 'Archived Cards' overview (which also shows card details). Driven by a new periodic Celery task, since this must happen automatically over time, not on a user action.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Board gets a new archive_after_days field (0 = disabled, default 0), editable via the existing create/edit board forms (same frontend pattern as stale_card_alert_hours)
- [ ] #2 Card gets is_archived (bool), archived_at (datetime), and moved_to_list_at (datetime, tracks when the card entered its CURRENT list) fields
- [ ] #3 moved_to_list_at is set/updated on every actual list change (move_card view and services.move_kanban_card), not on unrelated updates (comments, assignees, etc.)
- [ ] #4 New periodic Celery task archives cards sitting in a board's last list for longer than archive_after_days (only boards with archive_after_days > 0); added to CELERYBEAT_SCHEDULE in README.md per project convention
- [ ] #5 board_detail's card queryset excludes archived cards (is_archived=False) so they disappear from the normal board view
- [ ] #6 New 'Archived Cards' overview view/template lists archived cards for boards the user can view, with a link to open full card details (reusing the existing card modal)
- [ ] #7 Archived cards overview respects existing board view/write permissions (no new permission needed, uses can_user_view)
- [ ] #8 Tests cover: moved_to_list_at tracking, the archiving task's selection logic (respects archive_after_days per board, only targets the last list), board_detail excluding archived cards, and the overview view
- [ ] #9 CHANGELOG.md updated
- [ ] #10 Full test suite green on devauth sandbox
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented: Board.archive_after_days (0=disabled) editable via create/edit board forms (new 'Board Maintenance' card section). Card gained moved_to_list_at/is_archived/archived_at (migration 0024). move_card view and services.move_kanban_card now set moved_to_list_at on any actual list change (not on same-list reorders). New daily Celery task archive_done_cards (documented in README.md + testauth/settings/base.py CELERYBEAT_SCHEDULE) archives cards in a board's last list past the threshold, using Coalesce(moved_to_list_at, created_at) so cards created directly into the last list are handled correctly too. board_detail excludes archived cards. New archived_cards view+template (reuses card_item.html + a local cardModal shell, since summary.html's precedent lacked one) lists a board's archived cards with full detail access, gated by the existing can_user_view permission; linked via a new archive-icon button in the board header. 11 new tests, 132 passed, 8 skipped on devauth. Live-verified in browser: settings form field renders correctly, archived-cards overview page loads.
<!-- SECTION:NOTES:END -->
