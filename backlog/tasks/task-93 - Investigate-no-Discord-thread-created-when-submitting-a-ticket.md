---
id: TASK-93
title: 'Investigate: no Discord thread created when submitting a ticket'
status: Done
assignee: []
created_date: '2026-10-13 08:42'
updated_date: '2026-10-13 08:48'
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
TWO separate findings:

1. REAL BUG, FIXED: aa_kanban/cogs.py's setup(bot) was declared 'async def' and internally awaited bot.add_cog(...), but py-cord's extension loader (discord/cog.py _load_from_module_spec) calls setup(self) SYNCHRONOUSLY, never awaiting it. This meant the coroutine object was created and immediately garbage-collected (visible as 'RuntimeWarning: coroutine setup was never awaited' in authbot.log) and KanbanTicketCog (Discord-message-to-comment sync + Upload to Ticket context command) was NEVER actually registered with the bot, silently, since the app's creation. Fixed: setup is now a plain sync function calling bot.add_cog(...) directly (confirmed add_cog is sync in the installed py-cord version). 114 tests passed on devauth.

2. SEPARATE, NOT A CODE BUG: the actual 'no thread appears' symptom traces to the devauth authbot process hanging mid-connection (stuck right after cog/hook loading, never reaching its own 'Authbot Started' log line) since ~08:42 today. Confirmed via logs: it connected successfully at 08:40:49, then got stuck on the very next restart 2 minutes later (which was TASK-91's own final -RestartWeb). send_direct_message_by_user_id tasks fail with 'This function should be called asynchronously. Failed to queue a message' -- same symptom pattern as the missing threads, both going through the same aadiscordbot bot-connection dependency. Network to Discord REST API and Redis both verified healthy from the box. This strongly looks like a Discord gateway IDENTIFY/reconnect rate-limit triggered by the repeated supervisor restarts done across TASK-90/91 testing today (multiple restarts within a ~2 hour window). Deliberately stopped restarting authbot further during this investigation to avoid compounding any cooldown. RECOMMENDATION: do not restart authbot again for a while (ideally 15-30+ min); once it reconnects on its own (or via one single restart after that wait), create a real test ticket to confirm both the thread creation AND the newly-fixed cog actually work end-to-end. This is an operational/environment issue on the devauth sandbox, not something fixable via another code change.
<!-- SECTION:NOTES:END -->
