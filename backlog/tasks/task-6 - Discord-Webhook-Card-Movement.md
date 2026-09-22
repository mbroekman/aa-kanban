---
id: TASK-6
title: 'Discord Webhook: Card Movement'
status: Done
assignee: []
created_date: '2026-09-21 09:46'
updated_date: '2026-09-21 09:59'
labels: []
dependencies: []
ordinal: 14000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Trigger a Discord webhook when a card is moved between lists. Must use a separate webhook URL.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Webhook URL configurable, message sent on card move, tests pass
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added discord_webhook_cards to Board model and triggered it in move_card when card switches lists
<!-- SECTION:NOTES:END -->
