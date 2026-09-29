---
id: TASK-58
title: Fix card label color contrast and editability visibility
status: Done
assignee:
  - '@antigravity'
created_date: '2026-09-29 06:29'
updated_date: '2026-09-29 06:31'
labels: []
dependencies: []
type: bug
ordinal: 74000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

De kleurstelling van het card label klopt niet. Het is onduidelijk dat het label editable is. Daarnaast hebben in het dark theme de tekst en achtergrond dezelfde kleur waardoor de tekst onleesbaar is.

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->

- [x] #1 Card label heeft duidelijke visuele indicatie dat het editable is (bijv. border of hover state)
- [x] #2 In dark theme (en light theme) is er voldoende contrast tussen de tekst en de achtergrondkleur van het label

<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->

1. Locate the HTML template rendering the editable card label (likely card details modal). 2. Locate the associated CSS in kanban.css. 3. Adjust styles to add a visual cue for editability (e.g. dashed bottom border, hover effect, cursor pointer). 4. Ensure dark theme variables don't conflict, providing clear contrast for the text.

<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->

Added custom .editable-card-title CSS class to provide a dashed border and hover state for the card title input in the modal, making it obvious that it is editable. Added color: inherit to fix contrast issues in dark theme where the default input text color clashed with the transparent background.

<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

Fixed visibility of the editable card title by adding CSS styles for border, hover, and proper dark theme text contrast.

<!-- SECTION:FINAL_SUMMARY:END -->
