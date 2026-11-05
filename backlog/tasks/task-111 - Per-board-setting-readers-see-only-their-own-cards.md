---
id: TASK-111
title: 'Per-board setting: readers see only their own cards'
status: Done
assignee:
  - '@claude'
created_date: '2026-11-05 15:42'
updated_date: '2026-11-05 15:47'
labels: []
dependencies: []
priority: high
type: feature
ordinal: 125000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Members boards are open to everyone with Kanban access. Add a per-board setting so readers only see their own cards: cards they created or are assigned to (directly or through their team). Write groups, the board creator and board managers keep seeing all cards. On such a board, readers may add a card in the first column and update the title, description and comments of their own cards; moving, labels, assignees, team, colour and delete stay with the write groups.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Board has an own_cards_only setting, shown in the create and edit board forms
- [x] #2 Readers on such a board see only cards they created or are assigned to (directly or via a team), on the board page, archived cards, summary and dashboard counts
- [x] #3 Opening another reader's card returns 403
- [x] #4 Write groups, the board creator and board managers see all cards
- [x] #5 Readers can add a card in the first column only, and edit title, description and comments of their own cards
- [x] #6 Moving, labels, assignees, team, colour and delete remain write-group only
- [x] #7 Tests cover visibility and the edit rules; NL translations added
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
Board.own_cards_only field (migration 0028). Card.objects.owned_by(user) = created, assigned, or via team members/groups. Board.can_user_see_all_cards / visible_cards / can_user_add_card and Card.can_user_view / can_user_edit gate the views. Filter cards in board detail, archived cards, summary and board_stats. card_modal 403 for foreign cards; create_card, update_card and add_comment use the new checks. Templates show add-card on the first column and edit controls via can_edit_card.
<!-- SECTION:PLAN:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added the per-board 'Own cards only' setting. Readers on such a board see and open only cards they created or are assigned to (directly or via a team), can add cards in the first column and edit title, description and comments of their own cards; writers, the board creator and managers see everything. Board page, archived cards, summary and dashboard counts follow the setting. Verified on devauth: 15 new tests in test_own_cards.py, full suite 203 passed / 8 skipped, pre-commit clean, migration 0028 applied and makemigrations --check reports no changes. NL translations added.
<!-- SECTION:FINAL_SUMMARY:END -->
