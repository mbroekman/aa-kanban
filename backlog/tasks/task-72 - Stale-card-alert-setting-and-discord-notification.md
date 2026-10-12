---
id: TASK-72
title: Stale card alert setting and Discord notification
status: Done
assignee:
  - '@antigravity'
created_date: '2026-10-09 21:05'
updated_date: '2026-10-09 21:13'
labels:
  - feature
  - discord
dependencies: []
ordinal: 88000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add a setting to Board (`stale_card_alert_hours`) to detect cards that remain inactive for too long. When cards exceed this threshold, post an hourly bundled notification to the configured Discord channel (via bot or webhook) summarizing stale cards, column, duration, and assignees. Automatically exclude completed columns ('Done'/'Afgerond').
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->
- [x] #1 Field `stale_card_alert_hours` (PositiveIntegerField, default 0) and Discord alert configuration added to `Board` model
- [x] #2 Django migration generated and applied
- [x] #3 Board create/edit forms and templates updated with alert threshold fields
- [x] #4 Celery periodic task `check_stale_cards` implemented running hourly
- [x] #5 Stale card detection accounts for edits and comments, excluding completed columns
- [x] #6 Discord notification dispatches formatted summary to Discord channel or webhook
- [x] #7 Unit tests pass
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Extend `Board` model with `stale_card_alert_hours`, `discord_alert_channel_id`, and `discord_alert_webhook`.
2. Generate Django migration.
3. Update `views.py` and HTML templates (`create_board_form.html`, `edit_board_form.html`) with i18n support.
4. Implement periodic Celery task `check_stale_cards` and helper in `tasks.py` with Discord dispatch.
5. Register periodic task in Celery beat documentation.
6. Write unit tests in `aa_kanban/tests/` to validate stale card logic.
<!-- SECTION:PLAN:END -->
