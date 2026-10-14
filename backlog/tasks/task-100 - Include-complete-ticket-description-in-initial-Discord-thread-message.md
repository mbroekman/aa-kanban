---
id: TASK-100
title: Include complete ticket description in initial Discord thread message
status: Done
assignee: []
created_date: '2026-10-14 11:54'
updated_date: '2026-10-14 12:04'
labels: []
dependencies: []
priority: medium
type: feature
ordinal: 114000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Ensure all ticket text/description from a newly created ticket is included in the opening message of the Discord thread.
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

- Removed 500-character description truncation and code block wrapper in `aa_kanban/tasks.py::_create_discord_thread`.
- Added `_format_description_for_discord` to transform relative `/media/` links to absolute URLs and format markdown images nicely for Discord embedding.
- Added `_split_discord_message` helper to safely chunk messages that exceed Discord's 2000-character limit across multiple thread posts without 400 Bad Request errors.
- Added card label inclusion in the thread message header (`**Type:** <labels>`).
- Added comprehensive unit tests in `aa_kanban/tests/test_ticket_thread_notifications.py` covering full descriptions, labels, and 2000+ character auto-splitting. All 148 tests passing.

