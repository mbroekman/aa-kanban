---
id: TASK-5
title: 'Discord Webhook: Board Creation'
status: Done
assignee: []
created_date: '2026-09-21 09:46'
updated_date: '2026-09-21 09:59'
labels: []
dependencies: []
ordinal: 13000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Trigger a Discord webhook when a new board is created. The webhook URL should be separate from the card movement webhook.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Webhook URL configurable, message sent on board creation, tests pass
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Created KanbanSetting model with board_creation_webhook field and triggered it on create_board
<!-- SECTION:NOTES:END -->
