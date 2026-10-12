---
id: TASK-74
title: Add Auth Groups to KanbanTeam and auto-invite to Discord threads
status: Done
assignee:
  - '@antigravity'
created_date: '2026-10-09 21:30'
updated_date: '2026-10-09 21:40'
labels:
  - feature
  - discord
  - teams
dependencies: []
ordinal: 90000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Teams (`KanbanTeam`) previously only supported direct user assignment. Extend `KanbanTeam` with a ManyToMany relation to Django `Group` (Auth Groups) so entire groups can be assigned in frontend settings. Ensure automatic Discord thread invites collect all members from direct users and linked auth groups.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->
- [x] #1 `KanbanTeam` model expanded with `groups = ManyToManyField(Group)` and migration created
- [x] #2 Frontend settings UI updated to select and manage Auth Groups for a `KanbanTeam`
- [x] #3 Auto-invite in `tasks.py` collects both direct team members and members from linked auth groups
- [x] #4 Unit tests pass
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Add `groups = models.ManyToManyField(Group, blank=True, related_name="kanban_ticket_teams")` to `KanbanTeam` in `models.py`.
2. Generate migration `0020_kanbanteam_groups.py`.
3. Update `views_settings.py`, `urls.py`, and `team_users_modal.html` with endpoints for adding/removing auth groups to teams.
4. Update `tasks.py` to retrieve all members (`get_all_members()`).
5. Write unit tests and validate with test suite.
<!-- SECTION:PLAN:END -->
