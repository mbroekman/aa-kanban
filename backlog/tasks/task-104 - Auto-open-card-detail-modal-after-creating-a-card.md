---
id: TASK-104
title: Auto-open card detail modal after creating a card
status: Done
assignee: []
created_date: '2026-10-16 17:27'
updated_date: '2026-10-16 17:28'
labels: []
dependencies: []
ordinal: 118000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Wish: after submitting the inline 'New card title...' quick-add form, the card detail modal should open immediately instead of leaving the user to click the freshly added card themselves.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Creating a card via the column quick-add form opens its detail modal immediately
- [x] #2 The newly created card's hx-get content actually loads (no stuck loading spinner)
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented by flagging the create_card response with auto_open=True (card_item.html: data-auto-open="true") and auto-clicking that card once htmx has finished with it.

First attempt clicked the card synchronously inside the htmx:afterSwap handler (even deferred via setTimeout(fn, 0)) — this opened the Bootstrap modal shell (data-bs-toggle="modal" fires via its own delegated document listener) but never fired htmx's own hx-get request, leaving the modal stuck on its loading spinner forever. Root cause: htmx has not finished binding its click handler to the freshly swapped-in element by that point. Moved the auto-click to a htmx:afterSettle listener instead (fires once htmx has fully processed the new content, including binding hx-get) which fixed it. Verified live on devauth: creating a card now opens its modal with full details immediately, no spinner stuck.
<!-- SECTION:NOTES:END -->
