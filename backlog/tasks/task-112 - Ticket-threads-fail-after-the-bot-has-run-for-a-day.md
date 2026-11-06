---
id: TASK-112
title: Ticket threads fail after the bot has run for a day
status: Done
assignee: []
created_date: '2026-11-06 19:06'
updated_date: '2026-11-06 19:06'
labels: []
dependencies: []
ordinal: 126000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The Discord bot keeps its database connection for days. After the database's idle timeout the connection is gone, and _create_discord_thread fails with 'Lost connection to MySQL server', so cards get no ticket thread. Seen on production on 2026-11-06 (cards 153 and 157).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Bot tasks that use the database close a dropped connection first
- [x] #2 Test covers it
- [x] #3 Cards 153 and 157 on production got their threads
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
_create_discord_thread and _send_discord_thread_message now call close_old_connections first (via sync_to_async, same thread as the queries). Production: Auth bot restarted and the threads for cards 153 and 157 created.
<!-- SECTION:FINAL_SUMMARY:END -->
