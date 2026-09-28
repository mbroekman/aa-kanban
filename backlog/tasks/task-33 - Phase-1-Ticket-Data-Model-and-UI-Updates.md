---
id: TASK-33
title: 'Phase 1: Ticket Data Model and UI Updates'
status: Done
assignee: []
created_date: '2026-09-27 18:04'
updated_date: '2026-09-27 18:06'
labels: []
dependencies: []
ordinal: 41000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Extend the Card model with assigned_group and discord_thread_id. Update the Ticket submission UI so users can select the team.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Card model has new fields, database migration is created, Ticket form includes a dropdown for assigned_group, Kanban UI shows assigned group if present.
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added assigned_group and discord_thread_id to Card model, generated and applied migration. Updated Ticket Form UI to include team selection. Updated card views to display the assigned team badge.
<!-- SECTION:NOTES:END -->
