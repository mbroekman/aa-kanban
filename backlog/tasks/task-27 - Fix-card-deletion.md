---
id: TASK-27
title: Fix card deletion
status: Done
assignee: []
created_date: '2026-09-25 21:05'
updated_date: '2026-09-25 21:06'
labels: []
dependencies: []
ordinal: 35000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
User reports they cannot delete a card. Need to investigate if delete_card endpoint exists and is correctly hooked up in the UI.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Cards can be successfully deleted via UI
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Created the missing delete_card view, wired it up in urls.py, and added a delete button in the footer of the card modal. The card is removed from the DOM via HTMX, the modal is automatically closed, and the column count badges re-calculate seamlessly.
<!-- SECTION:NOTES:END -->
