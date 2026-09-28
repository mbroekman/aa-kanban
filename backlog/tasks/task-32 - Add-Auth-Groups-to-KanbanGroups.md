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
Momenteel kunnen we alleen individuele members lid maken van KanbanGroups. We willen ook de mogelijkheid hebben om Django Auth Groups (allianceauth groups) toe te voegen aan een KanbanGroup. Hierdoor kunnen grotere groepen members eenvoudiger geautoriseerd worden.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 KanbanGroup model is uitgebreid met een groups ManyToManyField naar Django Group, BoardQuerySet.visible_to en Board can_user_view/write houden rekening met auth group lidmaatschap, Frontend/Admin UI is geüpdatet zodat je auth groups kunt selecteren voor een KanbanGroup.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented Auth Group association for KanbanGroup. Created migration, updated models to use the new groups ManyToMany, and updated the UI (views_settings.py, group_users_modal.html, group_list.html) to manage both individual members and Auth Groups.
<!-- SECTION:NOTES:END -->
