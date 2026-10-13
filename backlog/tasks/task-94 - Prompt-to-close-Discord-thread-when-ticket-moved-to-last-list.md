---
id: TASK-94
title: Prompt to close Discord thread when ticket moved to last list
status: Done
assignee: []
created_date: '2026-10-13 15:10'
updated_date: '2026-10-13 15:14'
labels: []
dependencies: []
ordinal: 108000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
When a ticket card (one with a discord_thread_id) is moved into the LAST list/column of its board (e.g. a 'Done' column), the frontend should ask for confirmation to close the ticket's Discord thread. If confirmed, the thread is archived and locked via the Discord bot, with a closing message posted first. Declining leaves the thread open as-is. Only triggers on an actual list change (not a same-list reorder), mirroring the existing move-notification gating in move_card.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 move_card's JSON response includes a prompt_close_thread flag when: the card has a discord_thread_id, the move is to a different list than before, and the target list is the last list (by order) on the board
- [ ] #2 A confirmation modal appears client-side when prompt_close_thread is true, asking whether to close the Discord thread
- [ ] #3 Confirming posts to a new close_card_thread endpoint, which archives+locks the Discord thread via a new close_ticket_thread Celery task (mirrors the existing create_ticket_thread/notify_ticket_thread pattern), after posting a closing message into the thread
- [ ] #4 Declining the confirmation leaves the thread untouched and does not re-prompt until the card is moved out and back into the last list again
- [ ] #5 Regression tests added for both the move_card response flag and the close endpoint/task
- [ ] #6 CHANGELOG.md updated
- [ ] #7 Full test suite green on devauth sandbox
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented: move_card now returns prompt_close_thread=true in its JSON response when the card has a discord_thread_id, the move crosses lists, and the target list is the board's last list (by order). kanban.js's onEnd handler checks this flag and shows a new static Bootstrap modal (closeThreadModal in board_detail.html) asking for confirmation; confirming POSTs to a new close_card_thread endpoint, which dispatches a new close_ticket_thread Celery task (mirrors the existing create_ticket_thread/notify_ticket_thread aadiscordbot dispatch pattern). _close_discord_thread posts a closing message into the thread then calls thread.edit(archived=True, locked=True). 6 new tests covering: prompt flag on last-list move, no-prompt on non-last-list move, task dispatch, permission check, no-thread rejection, and the async archive/lock behavior itself. 121 passed, 8 skipped on devauth.
<!-- SECTION:NOTES:END -->
