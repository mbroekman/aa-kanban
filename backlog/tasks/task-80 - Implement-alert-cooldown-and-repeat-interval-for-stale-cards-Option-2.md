---
id: TASK-80
title: Implement alert cooldown and repeat interval for stale cards (Option 2)
status: Done
assignee: []
created_date: '2026-10-12 06:56'
updated_date: '2026-10-12 07:11'
labels: []
dependencies: []
ordinal: 96000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Prevent hourly alert spam for stale cards by adding last_stale_alert_at to Card and stale_card_repeat_hours to Board (default 24 hours, 0 = one-time alert). Cards will only be re-alerted once their repeat interval has expired.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Field stale_card_repeat_hours added to Board model and forms
- [x] #2 Field last_stale_alert_at added to Card model
- [x] #3 Django database migration generated and applied
- [x] #4 get_stale_cards() respects cooldown and repeat interval
- [x] #5 check_stale_cards() task updates last_stale_alert_at after dispatch
- [x] #6 Unit tests verify throttling, repeat interval, and one-time alert (0 hours)
<!-- AC:END -->
