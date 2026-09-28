---
id: TASK-53
title: Send Discord webhook notification on Card creation
status: Done
assignee: []
created_date: '2026-09-28 21:20'
updated_date: '2026-09-28 21:21'
labels: []
dependencies: []
ordinal: 65000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
When a new Card is created, a notification (ping) should be sent to the board`s discord_webhook_cards URL. This should preferably be handled asynchronously via a Celery task.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Creating a new Card triggers a webhook to the board`s discord_webhook_cards URL
- [ ] #2 The webhook message includes card details (title, board name, list name)
- [ ] #3 The webhook request is handled asynchronously (Celery)
- [ ] #4 1
- [ ] #5 2
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added discord webhook ping to views_api.card_create using send_discord_webhook. Kept it synchronous to match existing pattern in views.py and services.py.
<!-- SECTION:NOTES:END -->
