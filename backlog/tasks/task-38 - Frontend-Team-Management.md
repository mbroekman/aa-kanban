---
id: TASK-38
title: Frontend Team Management
status: Done
assignee: []
created_date: '2026-09-27 19:36'
updated_date: '2026-09-27 19:38'
labels: []
dependencies: []
ordinal: 46000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Move KanbanTeam management to the frontend settings page so functional settings are in the frontend.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 KanbanTeams can be created, edited, and deleted from the frontend Settings page; Users can be added/removed from KanbanTeams in the frontend.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Created KanbanTeam settings UI in frontend. Includes HTMX views for CRUD operations on Teams, modal for editing Team name and discord role ID, and modal for adding/removing individual users. Included OOB swaps for seamless updates.
<!-- SECTION:NOTES:END -->
