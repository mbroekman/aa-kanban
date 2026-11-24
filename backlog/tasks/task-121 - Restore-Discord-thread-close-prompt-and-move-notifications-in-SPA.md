---
id: TASK-121
title: Restore Discord thread close-prompt and move notifications in SPA
status: Done
assignee: []
created_date: '2026-11-24 21:00'
updated_date: '2026-11-24 21:00'
labels: []
dependencies: []
ordinal: 506000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
TASK-94's classic `move_card` view notifies a ticket card's Discord thread on
every list change and flags `prompt_close_thread` when the card lands in the
board's last list, prompting the user to archive+lock the thread. The SPA
migration (v2.0.0) never ported this to `api_move_card`: it only moved the
card and returned `{"ok": True}`, silently dropping the thread notification,
the card-creator notification, the board webhook on move, and the
close-thread prompt entirely. Restore full parity in the SPA.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 `api_move_card` ports the classic view's post-move logic exactly:
      `notify_card_creator` on any list change, `notify_ticket_thread` status
      update when the card has a `discord_thread_id`, the board's
      `discord_webhook_cards` notification, and `prompt_close_thread` in the
      JSON response when the move lands in the board's last list
- [x] #2 New `api_close_card_thread` endpoint (mirrors the classic
      `close_card_thread`): dispatches `close_ticket_thread` for a card's
      Discord thread, rejecting cards with no thread or no write permission
- [x] #3 `BoardView.tsx`'s drag-and-drop handler shows a confirmation dialog
      when `prompt_close_thread` is true, calling the new endpoint on confirm
      and leaving the thread open on decline
- [x] #4 New tests mirror the classic view's: notify-on-move, prompt on
      last-list move, no prompt without a thread/mid-board move, close-thread
      dispatch, permission check, no-thread rejection
- [x] #5 Full test suite green (run on devauth: local Windows run needs a
      real Redis the dev machine doesn't have)
- [x] #6 CHANGELOG updated, version bumped
<!-- AC:END -->
