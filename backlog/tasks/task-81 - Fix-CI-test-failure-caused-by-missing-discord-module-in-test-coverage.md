---
id: TASK-81
title: Fix CI test failure caused by missing discord module in test-coverage
status: Done
assignee: []
created_date: '2026-10-12 07:48'
updated_date: '2026-10-12 07:52'
labels: []
dependencies: []
type: bug
ordinal: 97000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Fix ModuleNotFoundError: No module named 'discord' in _create_discord_thread and _send_discord_thread_message when running tox tests without py-cord/aadiscordbot. Ensure graceful fallback and proper mocking in test_ticket_thread_notifications.py.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 tasks.py handles missing discord module gracefully without raising ModuleNotFoundError
- [x] #2 test_ticket_thread_notifications.py mocks discord module for thread creation and auto-invite tests
- [x] #3 All tests pass in clean test environment without py-cord installed
<!-- AC:END -->
