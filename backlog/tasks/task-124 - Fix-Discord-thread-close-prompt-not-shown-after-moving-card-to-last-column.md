---
id: TASK-124
title: Fix Discord thread close prompt not shown after moving card to last column
status: Done
assignee: []
created_date: '2026-11-26 17:55'
updated_date: '2026-11-26 18:05'
labels: []
dependencies: []
priority: high
type: bug
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
When a ticket card with a linked Discord thread is dragged to the board's last column (e.g. "Done"), the API returns `prompt_close_thread: true`, but the "Close Discord thread?" dialog never appeared, so the thread was never archived and locked.

Root cause: `BoardView.handleDragEnd` awaited `onReload()` before opening the prompt. `onReload` called `App.loadBoard`, which set `loadingBoard` and replaced `BoardView` with the loading spinner. The `BoardView` instance that set `closeThreadCardId` was unmounted and the freshly mounted one started with the prompt closed. Drag-and-drop (mouse and touch) is the only SPA route to the last column, so both desktop and iPad were affected.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Board reloads triggered from inside `BoardView` are silent and keep `BoardView` mounted
- [x] #2 The close-thread prompt is opened before the board data reload
- [x] #3 A failing close-thread request shows an error instead of failing silently
- [x] #4 SPA bundle rebuilt
<!-- AC:END -->
