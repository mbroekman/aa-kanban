---
id: TASK-87
title: >-
  Fix: card description becomes uneditable after save, Write/Preview toggle
  missing
status: Done
assignee: []
created_date: '2026-10-12 16:57'
updated_date: '2026-10-12 17:42'
labels: []
dependencies: []
ordinal: 101000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
After saving a card's description, the user can no longer edit it (likely description area replaced by rendered HTML view with no edit affordance left). Additionally, the Write/Preview toggle (and therefore the way to view an attached image vs raw markdown) introduced in TASK-77 is not showing up. Need to investigate card_modal_content.html, the description save endpoint in views_api.py, and kanban.js event wiring for the Write/Preview tabs and the rendered-description swap after save.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 After saving a card description, the user can click back into edit mode (Write tab) to change it again
- [ ] #2 The Write/Preview toggle is visible and functional in the card modal after the card has an existing description
- [ ] #3 Regression test added covering edit-after-save for card description
- [ ] #4 Full test suite green on devauth sandbox
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Root cause: after saving a description, the server only OOB-swapped the rendered text (#card-desc-rendered), leaving the Edit/Preview toggle buttons and a stale 'Add description' prompt dependent on client-side JS class toggling that could desync from the true server state. Fix: extracted the whole description block (toggle buttons, view box, edit form) into its own partial (card_description_block.html) and re-render it as ONE OOB swap after every save, so the UI is always 100% consistent with the saved state. Simplified kanban.js accordingly (removed the now-unnecessary client-side toggleCardDescMode('view') call after save). Added 2 regression tests. 107 passed, 8 skipped on devauth; live-verified via a second edit on an already-saved card.
<!-- SECTION:NOTES:END -->
