---
id: TASK-63
title: Remove ticket_channel_id from global settings
status: Done
assignee:
  - '@antigravity'
created_date: '2026-09-29 07:28'
updated_date: '2026-09-29 07:30'
labels: []
dependencies: []
type: chore
ordinal: 79000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The global ticket_channel_id is no longer needed since it was moved to the board level. Remove it from models, views, templates and tasks.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 ticket_channel_id removed from KanbanSetting
- [x] #2 ticket_channel_id removed from settings.html
- [x] #3 update_global_settings no longer processes ticket_channel_id
- [x] #4 tasks.py create_discord_thread only uses board.discord_ticket_channel_id
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Removed ticket_channel_id from KanbanSetting in models.py, generated and applied migration 0017. Removed the input field from settings.html and the processing logic from views_settings.py. Removed fallback logic in tasks.py so discord tickets only use the board's channel_id.
<!-- SECTION:NOTES:END -->
