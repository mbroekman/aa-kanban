---
id: TASK-91
title: Invite/remove Discord thread access via card Assignees
status: Done
assignee: []
created_date: '2026-10-12 20:42'
updated_date: '2026-10-12 20:46'
labels: []
dependencies: []
ordinal: 105000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Extend the existing card Assignee mechanism (already visible and persisted on every card) so that it also controls Discord thread membership for ticket cards, giving officers a single recorded place to grant/revoke access to a ticket's private Discord thread. When a user is added as an assignee on a card that has a discord_thread_id, their linked DiscordUser (if any) is automatically invited into the private thread. When removed as an assignee, they are automatically removed from the thread too (symmetric behavior, per explicit user decision).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 tasks.py: _send_discord_thread_message accepts invite_user_id and remove_user_id kwargs; when set and the user has a linked DiscordUser, it calls thread.add_user()/thread.remove_user() respectively
- [ ] #2 tasks.py: notify_ticket_thread celery task passes invite_user_id/remove_user_id through to the async handler
- [ ] #3 views_api.py: toggle_assignee posts a thread notification and invites the user's DiscordUser when adding an assignee to a card with a discord_thread_id
- [ ] #4 views_api.py: toggle_assignee posts a thread notification and removes the user's DiscordUser when removing an assignee from a card with a discord_thread_id
- [ ] #5 Regression tests added covering both invite-on-assign and remove-on-unassign
- [ ] #6 CHANGELOG.md and User Manual updated to document that assigning someone to a ticket grants them Discord thread access
- [ ] #7 Full test suite green on devauth sandbox
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented: tasks.py _send_discord_thread_message gained invite_user_id/remove_user_id kwargs (mirrors the existing team_id pattern) that look up the target user's DiscordUser and call thread.add_user()/thread.remove_user(). notify_ticket_thread passes these through. views_api.py toggle_assignee now posts a thread notification + invite_user_id when adding an assignee to a card with discord_thread_id, and remove_user_id when removing one -- symmetric access (per explicit user decision: unassign also revokes thread access). 3 new tests (view-layer dispatch for both directions + async-level add_user/remove_user verification) plus 1 existing test's kwargs assertion updated. 111 passed, 8 skipped. NOTE: User Manual (backlog/docs/doc-4) update deferred -- a concurrent background process (TASK-89) is actively rewriting that file with a large uncommitted diff; editing it now risked conflicting with that in-progress work. Follow up once TASK-89's changes are committed.
<!-- SECTION:NOTES:END -->
