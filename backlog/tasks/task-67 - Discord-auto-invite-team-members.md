---
id: TASK-67
title: Discord auto-invite team members
status: Done
assignee: []
created_date: '2026-09-29 15:24'
labels: []
dependencies: []
type: feature
ordinal: 83000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

Automatically invite users connected to an assigned team to the Discord thread upon ticket creation.

<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->

Added logic in aa_kanban.tasks.\_create_discord_thread to map team members to DiscordUsers and use thread.add_user() to invite them automatically. Version bumped to 0.11.0.

<!-- SECTION:NOTES:END -->
