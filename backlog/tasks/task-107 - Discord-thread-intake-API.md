---
id: TASK-107
title: Discord thread intake API
status: In Progress
assignee: []
created_date: '2026-11-02 13:18'
updated_date: '2026-11-02 16:03'
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
- [x] #1 Valid key creates a card with thread title, starter message, author and thread link; discord_thread_id set
- [x] #2 Second call for the same thread returns the existing card
- [x] #3 Invalid or missing key gives 401; unknown board 404
- [x] #4 Unknown labels/team are skipped and reported
- [x] #5 Tests, NL translations, CHANGELOG and manual updated
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
views_intake.py + IntakeApiKey (migration 0026, admin with one-time key display and regenerate action). URL is last in urls.py: AA's decorate_url_patterns returns instead of continuing after an excluded view, so patterns after it would lose the login check; test guards this. Needs aa_kanban in APPS_WITH_PUBLIC_VIEWS (server local.py) to be reachable - not changed on devauth yet, waiting for the user. Deployed to devauth from a clean clone (other uncommitted work in this repo left alone). 166 tests pass on devauth.

2026-11-02: aa_kanban added to APPS_WITH_PUBLIC_VIEWS on devauth (backup local.py.bak-<timestamp>). Verified: intake POST without key = 401; /kanban/ and /kanban/summary/ still 302 to login.
<!-- SECTION:NOTES:END -->
