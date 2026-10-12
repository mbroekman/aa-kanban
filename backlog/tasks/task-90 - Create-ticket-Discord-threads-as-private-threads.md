---
id: TASK-90
title: Create ticket Discord threads as private threads
status: Done
assignee: []
created_date: '2026-10-12 19:19'
updated_date: '2026-10-12 19:22'
labels: []
dependencies: []
ordinal: 104000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Ticket Discord threads are currently created via Message.create_thread() on a message posted publicly in the ticket channel (tasks.py:242-243). Per the Discord API, create_thread() on a Message can only ever produce a PUBLIC thread (visible to anyone who can see the parent channel) -- there is no way to make a thread private from an existing message. The requirement is for ticket threads to be private: only the ticket creator, the bot, and the assigned team's Discord users should be able to see the thread. Need to switch to TextChannel.create_thread(type=discord.ChannelType.private_thread), post the starter message into the new thread directly (not into the channel), and explicitly add the creator (not just the assigned team) to the thread.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 _create_discord_thread creates the thread via channel.create_thread(..., type=discord.ChannelType.private_thread) instead of starter_message.create_thread()
- [ ] #2 The starter ticket-info message is sent into the newly created private thread, not posted publicly in the channel
- [ ] #3 The ticket creator's Discord user is explicitly added to the thread via thread.add_user(), in addition to the existing assigned-team auto-invite
- [ ] #4 Existing test_ticket_thread_notifications.py tests updated/passing; new test asserts type=discord.ChannelType.private_thread is passed and the creator is added
- [ ] #5 CHANGELOG.md updated
- [ ] #6 Full test suite green on devauth sandbox
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented: _create_discord_thread now calls channel.create_thread(name=thread_name, type=discord.ChannelType.private_thread, invitable=False) instead of starter_message.create_thread() (which can only ever produce a public thread per the Discord API). The starter ticket-info message is sent into the new thread via thread.send() instead of posted publicly in the channel. The ticket creator (resolved via the existing creator_discord lookup, now initialized to None to avoid a NameError when DiscordUser is unavailable) is explicitly invited via thread.add_user(), in addition to the existing assigned-team auto-invite. Updated the existing auto-invite test to mock channel.create_thread/thread.send instead of message.create_thread, added assertions for type=private_thread and invitable=False, plus a new dedicated test for the creator invite. 108 passed, 8 skipped on devauth.
<!-- SECTION:NOTES:END -->
