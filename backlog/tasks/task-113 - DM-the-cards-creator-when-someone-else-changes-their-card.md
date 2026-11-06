---
id: TASK-113
title: DM the card's creator when someone else changes their card
status: Done
assignee: []
created_date: '2026-11-06 19:16'
updated_date: '2026-11-06 19:16'
labels: []
dependencies: []
ordinal: 127000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
The creator of a card gets a Discord DM when someone else moves it, comments on it, or changes its assignees, labels or team. Started in an earlier session (code and tests uncommitted in the G: checkout); finished here.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Creator gets a DM for move, comment, assignee, label and team changes made by someone else
- [x] #2 No DM for own changes, while the creator is an assignee or team member, or when the change is also posted in the card's ticket thread
- [x] #3 Dutch translations
- [x] #4 Tests, CHANGELOG, README and manual updated
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
notify_card_creator in tasks.py, called from move_card, add_comment, toggle_assignee, toggle_label, update_card_team and services.move_kanban_card. Added: skip when the card has a ticket thread and the change is posted there (posted_in_thread, False for comments). 10 tests in test_card_creator_notifications.py; NL po/mo via polib.
<!-- SECTION:FINAL_SUMMARY:END -->
