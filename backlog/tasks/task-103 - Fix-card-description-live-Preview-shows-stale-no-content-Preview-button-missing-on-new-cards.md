---
id: TASK-103
title: >-
  Fix: card description live Preview shows stale/no content, Preview button
  missing on new cards
status: Done
assignee: []
created_date: '2026-10-16 11:12'
updated_date: '2026-10-16 17:28'
labels:
  - bug
dependencies: []
ordinal: 117000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Two related preview bugs in the card modal description editor (card_description_block.html / kanban.js toggleCardDescMode), distinct from the ticket submission form's working AJAX preview (ticket_form.html toggleTicketDescTab):

1. Preview button never appears for a brand-new/empty card description: #btn-card-desc-view has a hardcoded 'd-none' class in the template regardless of state. For an existing card (has description), initial render is View mode and the Edit click correctly unhides the Preview button via JS. But for a NEW card with no description yet, the template renders directly into edit mode server-side (via the 'not card.description' condition), bypassing toggleCardDescMode entirely -- so the Preview button's unhide logic never runs and it stays hidden. This is the 'no preview button at all' symptom seen in dev when testing on a fresh ticket/card.

2. Clicking Preview (toggleCardDescMode('view') in kanban.js) does not actually render current unsaved textarea content -- it just un-hides #card-desc-view, which still contains the server-rendered HTML from page load (the last SAVED description). So Preview only ever reflects the previously saved version, which is why it 'only works after you've saved' in production -- it isn't live at all, unlike the ticket form's correct implementation which POSTs to aa_kanban:preview_markdown and injects the response.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 After saving a card description, the user can click back into edit mode (Write tab) to change it again
- [x] #2 The Write/Preview toggle is visible and functional in the card modal, including for a brand-new card with no description yet
- [x] #3 Clicking Preview renders the current unsaved textarea content live, not the last-saved content
- [x] #4 Pasting/attaching a second image never collides with the first via a shared placeholder string
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Two root causes fixed in the card modal's description editor (card_description_block.html / kanban.js toggleCardDescMode), distinct from the ticket submission form's already-correct implementation:

1. #btn-card-desc-view (the Preview button) had a hardcoded d-none class regardless of state, so it never appeared for a brand-new card with no description yet (template rendered straight into edit mode server-side, bypassing the JS toggle that would normally unhide it). Fixed by making its d-none conditional on card.description, mirroring the edit form's own condition.
2. toggleCardDescMode('view') only ever un-hid the server-rendered HTML from page load -- it never reflected the current unsaved textarea content, so Preview appeared to 'only work after saving'. Now POSTs the live textarea value to the existing preview_markdown endpoint and injects the response, matching the ticket form's approach. Added a data-preview-url attribute to the textarea for this.
3. Hardened uploadAndInsert()'s placeholder text (previously just the filename, e.g. 'Uploading image.png...' -- clipboard pastes are always named image.png by the browser) with a unique monotonic counter token, so two concurrent uploads can never land on an identical placeholder string and risk the wrong one being replaced first.

Verified live on devauth with real paste/attach/preview flows including two-image descriptions. Full suite 149 passed/8 skipped at the time.
<!-- SECTION:NOTES:END -->
