---
id: TASK-37
title: Decouple Ticket Teams from KanbanGroups
status: Done
assignee: []
created_date: '2026-09-27 19:26'
updated_date: '2026-09-27 19:31'
labels: []
dependencies: []
ordinal: 45000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Create a new KanbanTeam model for assigning tickets, instead of reusing KanbanGroup which is meant for board access control.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 KanbanTeam model exists, Card uses assigned_team instead of assigned_group, Settings UI manages Teams instead of Groups for assignments
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Created KanbanTeam model. Renamed Card.assigned_group to Card.assigned_team and updated relation. Updated views.py, tasks.py, and templates to use KanbanTeam instead of KanbanGroup for ticket routing. Registered KanbanGroup and KanbanTeam in admin.py.
<!-- SECTION:NOTES:END -->
