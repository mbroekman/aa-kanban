---
id: TASK-55
title: Enhance card assignments with teams and search
status: Done
assignee: []
created_date: '2026-09-28 21:25'
updated_date: '2026-09-28 21:30'
labels: []
dependencies: []
ordinal: 67000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

Update the card modal to allow assigning a team, and add a search function (Select2) to the members list when assigning users.

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->

- [ ] #1 Users can assign a KanbanTeam to a card from the card modal
- [ ] #2 The list of users to assign has a search function (e.g. Select2)
- [ ] #3 Updating the team saves correctly to the database
- [ ] #4 1
- [ ] #5 2
- [ ] #6 3

<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->

Added team assignment dropdown using a new card_team partial and update_card_team view. Added a native JS search input to the assignees dropdown and removed the 20-user limit.

<!-- SECTION:NOTES:END -->
