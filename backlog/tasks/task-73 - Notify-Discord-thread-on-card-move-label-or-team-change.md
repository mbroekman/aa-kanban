---
id: TASK-73
title: Notify Discord thread on card move, label, or team change
status: Done
assignee:
  - '@antigravity'
created_date: '2026-10-09 21:20'
updated_date: '2026-10-09 21:23'
labels:
  - feature
  - discord
  - tickets
dependencies: []
ordinal: 89000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
When a ticket card is linked to a Discord thread (`discord_thread_id`), notify the thread immediately on changes:
1. When card is moved to another list/column (e.g. Backlog to In Progress).
2. When assigned team changes (or is cleared), including role mention and auto-invite of new team members.
3. When labels are added or removed from the card.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->
- [x] #1 Celery task `notify_ticket_thread` and async bot helper implemented to post messages in Discord threads
- [x] #2 Moving a card (`move_card` and `services.move_kanban_card`) posts a status update to the thread
- [x] #3 Changing card team (`update_card_team`) posts a team update to the thread with member auto-invites
- [x] #4 Adding or removing a label (`toggle_label`) posts a label update to the thread
- [x] #5 Unit tests pass
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add `_send_discord_thread_message` async runner and `notify_ticket_thread` task in `tasks.py`.
2. Update `views_api.py` in `move_card`, `update_card_team`, and `toggle_label` to invoke `notify_ticket_thread.delay(...)`.
3. Update `services.py` in `move_kanban_card`.
4. Add translations (EN & NL) for thread notification strings.
5. Write unit tests in `aa_kanban/tests/` verifying all scenarios.
<!-- SECTION:PLAN:END -->
