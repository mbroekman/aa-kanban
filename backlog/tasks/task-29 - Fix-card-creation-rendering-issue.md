---
id: TASK-29
title: Fix card creation rendering issue
status: Done
assignee: []
created_date: '2026-09-26 16:07'
updated_date: '2026-09-26 16:09'
labels: []
dependencies: []
ordinal: 37000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
User reports that newly created cards only show text, not the complete card format. Need to check how create_card returns its payload.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 New cards render as full cards
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Removed hx_oob arguments from create_card view. The HTMX form already correctly targets the list via hx-swap='beforeend', so returning an OOB element caused it to be stripped out, rendering just an empty/broken response.
<!-- SECTION:NOTES:END -->
