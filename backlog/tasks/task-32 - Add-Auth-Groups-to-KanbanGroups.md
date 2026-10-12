---
id: TASK-32
title: Add Auth Groups to KanbanGroups
status: Done
assignee: []
created_date: '2026-09-27 17:17'
updated_date: '2026-09-27 17:47'
labels: []
dependencies: []
ordinal: 40000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Enable associating Django Auth Groups with KanbanGroups, allowing all members of selected auth groups to automatically inherit board access.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->
- [x] #1 KanbanGroup model expanded with groups ManyToManyField to Django Group
- [x] #2 BoardQuerySet.visible_to and Board permissions account for auth group membership
- [x] #3 Frontend Settings UI updated to manage linked auth groups for KanbanGroups
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented Auth Group association for KanbanGroup. Created migration, updated models to use the new groups ManyToMany, and updated the UI (views_settings.py, group_users_modal.html, group_list.html) to manage both individual members and Auth Groups.
<!-- SECTION:NOTES:END -->
