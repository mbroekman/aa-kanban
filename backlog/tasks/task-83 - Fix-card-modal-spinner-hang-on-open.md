---
id: TASK-83
title: Fix card modal spinner hang on open
status: Done
priority: high
created: 2026-10-12
assigned_to: Antigravity
labels:
  - bug
  - ui
  - bootstrap5
  - htmx
---

## Description
When clicking on a Kanban card to view its details, the Bootstrap 5 `#cardModal` opens with its initial loading spinner (`<div class="spinner-border">`), but the modal body never swaps or loads the card content. This issue occurs due to a conflict when combining Bootstrap's `data-bs-toggle="modal"` with HTMX's `hx-get` on the same SortableJS drag handle element (`.kanban-card`), causing the HTMX request to either be swallowed or not fired. Additionally, when `#cardModal` closes and reopens, previous content or loading states need clean lifecycle management.

## Acceptance Criteria
- [x] Add explicit Bootstrap modal event handler (`show.bs.modal`) on `#cardModal` to trigger `htmx.ajax('GET', modalUrl, {target: '#cardModalBody', swap: 'innerHTML'})` from the clicked card's `data-modal-url`.
- [x] Reset `#cardModalBody` to the loading spinner on `show.bs.modal` and `hidden.bs.modal` to prevent flashing stale card data between different cards.
- [x] Update `card_item.html` with `data-modal-url` and ensure proper HTMX/Bootstrap attributes on the card markup.
- [x] Remove `!canWrite` early return in `kanban.js` so modal and event handlers execute for all users (both write and read-only).
- [x] Verify card modals load instantly and reliably upon clicking on `devauth.spral.space`.
- [x] Run pytest, type checks, linting, update changelog and synchronize workspace.
