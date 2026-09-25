---
id: TASK-25
title: Assign background color to cards
status: Done
assignee: []
created_date: '2026-09-25 19:56'
updated_date: '2026-09-25 20:06'
labels: []
dependencies: []
ordinal: 33000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Allow users to assign a background color to individual records (cards). This involves adding a 'color' field to the Card model, updating the card creation/editing forms to support color selection, and applying the color to the card item in the frontend.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Card model has a color field\nCard modal allows selecting a color\nCard item displays the assigned color\nColor is preserved upon save and reload
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added a 'color' field to the Card model with Bootstrap color choices. Created an endpoint update_card_color and integrated a quick color picker into the Card modal. Cards now render with text-bg-{color}.
<!-- SECTION:NOTES:END -->
