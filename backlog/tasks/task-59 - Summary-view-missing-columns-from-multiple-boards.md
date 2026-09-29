---
id: TASK-59
title: Summary view missing columns from multiple boards
status: Done
assignee:
  - '@antigravity'
created_date: '2026-09-29 06:36'
updated_date: '2026-09-29 06:37'
labels: []
dependencies: []
type: bug
ordinal: 75000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

De summary view geeft niet de kolommen weer van alle boards, maar toont alleen de kolommen van het eerste board. Dit moet worden opgelost zodat de weergave kaarten en kolommen correct per board groepeert of in ieder geval de juiste kolommen van alle boards toont.

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->

- [x] #1 Summary view toont de juiste lijsten/kolommen voor elk zichtbaar board
- [x] #2 Kaarten worden correct ondergebracht bij hun respectievelijke kolommen van alle boards

<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->

1. Check how views.py retrieves data for the summary view. 2. Look at summary.html to see how it iterates through columns/boards. 3. Fix the context/iteration logic so all boards and their columns are represented correctly.

<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->

Updated summary.html. Removed the hardcoded default_columns array which forced the grid to only show columns matching 'Backlog', 'To Do', etc. Instead, the grid now dynamically loops over board.lists.all, showing the exact columns (and their corresponding cards) for each specific board. The CSS grid-template-columns is now dynamically calculated based on the number of columns of that board.

<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->

Summary view now correctly renders the actual columns and cards for each individual board dynamically.

<!-- SECTION:FINAL_SUMMARY:END -->
