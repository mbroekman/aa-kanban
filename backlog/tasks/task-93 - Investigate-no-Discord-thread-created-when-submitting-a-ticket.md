---
id: TASK-93
title: 'Investigate: no Discord thread created when submitting a ticket'
status: Done
assignee: []
created_date: '2026-10-13 08:42'
updated_date: '2026-10-13 11:08'
labels: []
dependencies: []
ordinal: 107000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
User reports: after TASK-90 (private thread creation) and TASK-91 (assignee-driven invite) shipped, submitting a ticket no longer results in a visible Discord thread. User has exactly 1 ticket board and 1 team configured. Need to find the actual failure point (config, permissions, py-cord version incompatibility with the new private-thread call, or something else) via live log/shell investigation on devauth.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Root cause identified via actual logs/shell inspection, not speculation
- [ ] #2 Fix applied and live-verified (a real test ticket produces a visible, accessible Discord thread)
- [ ] #3 Regression test added if the root cause is something existing tests could not catch
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
CORRECTED FINAL ROOT CAUSE (previous notes about rate-limiting/on_ready-timing were WRONG -- based on checking the wrong log file, see below):

The real cause has NOTHING to do with public vs private threads, my restarts, or rate-limiting. Found in the CORRECT log file (log/discord_bot.log -- aadiscordbot's logger is routed there via a dedicated Django LOGGING handler 'bot_log_file', NOT to authbot.log which only captures raw stdout/print/stderr):

discord.errors.LoginFailure: Improper token has been passed.
ERROR [aadiscordbot.bot] Unable to start bot! going to sleep for 2 min. Improper token has been passed.

The bot's DISCORD_BOT_TOKEN (hardcoded in myauth/settings/local.py:121 on devauth) is being rejected by Discord's API with 401 Unauthorized at login. The bot has NEVER successfully reached on_ready in the entire log retention window (confirmed: zero occurrences of 'Starting on_ready' ever) -- this is a pre-existing, long-standing devauth credentials issue, unrelated to TASK-90/91/93 entirely. It perfectly explains why webhook notifications (plain HTTP POST, no bot token needed) always worked while thread creation and any other bot-dependent feature (DMs, cog commands) never could.

LESSON LEARNED (for future investigations): aadiscordbot has its OWN Django logger ('aadiscordbot') explicitly routed to log/discord_bot.log via LOGGING['loggers']['aadiscordbot'] in settings/local.py -- NOT log/authbot.log (which only captures the process's raw stdout/stderr, i.e. print() statements and uncaught warnings, not Python logging calls). Always check discord_bot.log first for any aadiscordbot/bot-connection issue.

ACTION NEEDED (user, not a code fix): obtain a fresh valid bot token from the Discord Developer Portal and update DISCORD_BOT_TOKEN in myauth/settings/local.py on devauth, then restart myauth:authbot. This is unrelated to aa-kanban's code; the TASK-93 cog setup() fix (sync vs async) remains valid and committed regardless.
<!-- SECTION:NOTES:END -->
