---
id: TASK-60
title: Configure Discord thread channel ID per ticket board
status: Done
assignee:
  - '@antigravity'
created_date: '2026-09-29 06:47'
updated_date: '2026-09-29 06:49'
labels: []
dependencies: []
type: feature
ordinal: 76000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Allow specifying a Discord channel ID per ticket board for ticket thread creation instead of relying strictly on a global setting.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->
- [x] #1 Board model includes discord_ticket_channel_id field
- [x] #2 Creating a ticket spawns the thread in the board's specific channel
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added discord_ticket_channel_id to Board model and updated ticket creation to respect board channel.
<!-- SECTION:NOTES:END -->
