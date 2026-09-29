---
id: TASK-68
title: Fix Discord thread creation silent failures
status: Done
assignee: []
created_date: '2026-09-29 15:24'
labels: []
dependencies: []
type: bug
ordinal: 84000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Fix issues where ticket thread creation failed silently due to incorrect Celery queue routing and missing bot channel cache.
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Explicitly passed queue='aadiscordbot' to apply_async. Added fallback to bot.fetch_channel if bot.get_channel fails. Added task_kwargs={} to apply_async payload to satisfy bot_tasks signature. Bumped version to 0.10.1 and 0.10.2.
<!-- SECTION:NOTES:END -->
