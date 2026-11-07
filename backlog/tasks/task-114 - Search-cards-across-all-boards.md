---
id: TASK-114
title: Search cards across all boards
status: Done
assignee: []
created_date: '2026-11-07 08:50'
updated_date: '2026-11-07 08:50'
labels: []
dependencies: []
ordinal: 128000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Users can only look inside one board at a time. Add one search that covers every board the user can see, with results linking to the card.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Search box on the dashboard and in every board header
- [x] #2 Searches title, description, comments, assignee/creator/comment-author names, labels, team and card number; every word must match
- [x] #3 Same visibility as the boards: no hidden boards, own-cards-only boards show readers only their cards, archived boards only for managers and the creator
- [x] #4 Archived cards only with 'Include archived cards'
- [x] #5 Results link to the card on its board or archive page; max 100 results, title matches first
- [x] #6 Dutch translations, tests, manual, README and CHANGELOG
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
aa_kanban/search.py (search_cards, searchable_boards, snippets), view 'search' at /kanban/search/, templates search.html and partials/search_form.html (included on index and board header), highlight filter in kanban_tags. Archived results link to the archive page with ?card=, which kanban.js already opens. 16 tests in test_search.py.
<!-- SECTION:FINAL_SUMMARY:END -->
