---
id: TASK-96
title: Fix Comment.objects.create() wrong kwargs in cogs.py Discord sync
status: Done
assignee: []
created_date: '2026-10-13 20:18'
updated_date: '2026-10-13 20:25'
labels: []
dependencies: []
ordinal: 110000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Both sync_ticket_comment and upload_to_ticket in aa_kanban/cogs.py call Comment.objects.create(card=card, created_by=user, content=content), but the Comment model's actual fields are author and text. This raises TypeError every time, silently swallowed by except Exception, so Discord-to-Kanban comment sync has never actually worked. Found live on production (Game of Drones/3gods server) during DM delivery diagnostics. Fix: rename kwargs to author/text, make Comment.author nullable (the code supports unlinked Discord users posting with no AA account), add a migration, and update card_comments.html to render gracefully when author is null.
<!-- SECTION:DESCRIPTION:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Fixed: cogs.py's two Comment.objects.create() calls now use author=/text= (matching the model) instead of the stale created_by=/content=. Made Comment.author nullable (migration 0025) since unlinked Discord users intentionally post with no linked AA account. Updated card_comments.html to show a Discord icon fallback instead of a blank username when author is null. Added regression test in test_models.py. 133 passed, 8 skipped on devauth sandbox.
<!-- SECTION:NOTES:END -->
