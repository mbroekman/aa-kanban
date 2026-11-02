---
id: TASK-107
title: Discord thread intake API
status: To Do
assignee: []
created_date: '2026-11-02 13:18'
labels: []
dependencies: []
ordinal: 121000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Endpoint for the discord-thread-router (githubDiscordBOT doc-1): POST /kanban/api/intake/discord-thread/ with Bearer API key. Creates a card on the given board/list with labels and team, sets discord_thread_id. Idempotent on thread id. Creator = Auth user linked to the Discord id, else service user 'Discord intake'. API keys managed in admin (hashed).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Valid key creates a card with thread title, starter message, author and thread link; discord_thread_id set
- [ ] #2 Second call for the same thread returns the existing card
- [ ] #3 Invalid or missing key gives 401; unknown board 404
- [ ] #4 Unknown labels/team are skipped and reported
- [ ] #5 Tests, NL translations, CHANGELOG and manual updated
<!-- AC:END -->
