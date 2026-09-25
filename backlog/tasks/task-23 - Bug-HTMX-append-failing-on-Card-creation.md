---
id: TASK-23
title: 'Bug: HTMX append failing on Card creation'
status: Done
assignee: []
created_date: '2026-09-25 13:39'
updated_date: '2026-09-25 13:52'
labels: []
dependencies: []
ordinal: 31000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
When adding a new card, the newly created record is not appended dynamically to the column. The user has to manually refresh the page to see the new card. This breaks the expected HTMX/async behavior.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
-[x] #1 New card appears instantly in the list after submission without full page refresh
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Fixed HTMX swap issue on card creation by using a robust hx-swap-oob. When creating a card, views_api.py now passes hx_oob=True, and card_item.html forces insertion into #list-cards-{{ card.list_id }} using 'beforeend'. This bypasses any client-side target ambiguity or race conditions with kanban.js.
<!-- SECTION:NOTES:END -->
