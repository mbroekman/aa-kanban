---
id: TASK-87
title: >-
  Fix: card description becomes uneditable after save, Write/Preview toggle
  missing
status: Done
assignee: []
created_date: '2026-10-12 16:57'
updated_date: '2026-10-12 18:32'
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
ROOT CAUSE CORRECTION: the OOB full-block re-render (first fix) was a legitimate robustness improvement but NOT the actual cause of the reported symptom. Live browser testing on devauth revealed the true cause: kanban.css's dark-theme override for .btn-outline-secondary targeted [data-bs-theme="dark"], but this Alliance Auth instance sets html[data-theme="darkly"] instead (confirmed via getComputedStyle: button color/border were both #444, i.e. invisible against the dark background). The override never applied, making Edit/Preview/Attach Image buttons present and functional but practically invisible. Fixed the CSS selector to also match html[data-theme="darkly"] (same pattern already used in aa-recruitment's styles.html). Also caught and fixed a second, unrelated bug in my own deploy workflow: editing CSS requires sandbox-sync.ps1 -CollectStatic (not just a restart) because of Django's ManifestStaticFilesStorage hashed filenames -- forgetting it served a stale hashed CSS file despite the restart. Live-verified via Chrome on devauth: Edit/Preview/Attach Image buttons now render with clear contrast (confirmed via getComputedStyle), full edit-after-save cycle works. 107 passed, 8 skipped.
<!-- SECTION:NOTES:END -->
