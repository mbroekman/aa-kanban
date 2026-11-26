---
id: TASK-124
title: Close Discord thread automatically when a card is moved to the last column
status: Done
assignee: []
created_date: '2026-11-26 17:55'
updated_date: '2026-11-26 18:20'
labels: []
dependencies: []
priority: high
type: bug
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
When a ticket card with a linked Discord thread is dragged to the board's last column (e.g. "Done"), the API returns `prompt_close_thread: true`, but the "Close Discord thread?" dialog never appeared, so the thread was never archived and locked.

Root cause: `BoardView.handleDragEnd` awaited `onReload()` before opening the prompt. `onReload` called `App.loadBoard`, which set `loadingBoard` and replaced `BoardView` with the loading spinner. The `BoardView` instance that set `closeThreadCardId` was unmounted and the freshly mounted one started with the prompt closed. Drag-and-drop (mouse and touch) is the only SPA route to the last column, so both desktop and iPad were affected.

Follow-up decision (Machiel): close the thread automatically instead of prompting. When a ticket card lands in the board's last column, the status update and a closing notice are posted and the thread is archived and locked, from every move path (SPA, classic view, `move_kanban_card` service).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Board reloads triggered from inside `BoardView` are silent and keep `BoardView` mounted
- [x] #2 Moving a ticket card to the last column closes its Discord thread automatically (no prompt), with a closing notice
- [x] #3 The status update is posted before the closing notice, in the same bot task
- [x] #4 Works for the SPA move, the classic move view and the move_kanban_card service
- [x] #5 Tests updated and added; SPA bundle rebuilt
<!-- AC:END -->
