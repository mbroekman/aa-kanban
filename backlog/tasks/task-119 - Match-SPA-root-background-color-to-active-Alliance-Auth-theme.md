---
id: TASK-119
title: Match SPA root background color to active Alliance Auth theme
status: Done
assignee: []
created_date: '2026-11-20 11:10'
updated_date: '2026-11-20 11:10'
labels: []
dependencies: []
ordinal: 133000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The Kanban SPA root (`.aa-spa-root`) hardcodes `--background` to two fixed
oklch values (one for light, one for `.dark`). Alliance Auth supports many
different Bootstrap sub-themes (bootstrap, flatly, darkly, cerulean, ...),
each with its own distinct body background color, so the hardcoded values
only roughly approximate the real page background and visibly mismatch on
non-default themes. Only the background color should track the live theme;
foreground/card/border/etc. must stay exactly as they are now.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 `main.tsx` reads `document.body`'s live computed background-color and applies it as an inline `--background` override on the SPA mount element
- [x] #2 The override re-applies whenever Alliance Auth's theme changes (reuses the existing MutationObserver)
- [x] #3 Falls back to the existing hardcoded light/dark `--background` values when the computed background is transparent/unreadable
- [x] #4 No change to `--foreground`, `--card`, `--border`, or any other token; dark-mode class toggling logic unchanged
- [x] #5 `npm run build` succeeds and the rebuilt `assets/index.js`/`index.css` are committed
<!-- AC:END -->
