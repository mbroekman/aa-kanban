---
id: TASK-84
title: >-
  Move board-management permission (manage_boards) to frontend KanbanGroup
  control
status: Done
assignee: []
created_date: '2026-10-12 14:57'
updated_date: '2026-10-12 15:08'
labels: []
dependencies: []
ordinal: 98000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Currently, granting the ability to manage boards (settings page, create/edit/delete boards) requires the Django permission 'aa_kanban.manage_boards', which can only be assigned via Django's native auth Group in the technical /admin/ panel. This violates ADR-006 (functional configuration must live in the frontend, not Django admin). Per ADR-007-style layered access, board-level view/write access already works through the custom KanbanGroup model managed entirely in the frontend settings UI. Add a 'can_manage_boards' flag to KanbanGroup so that officers can grant board-management rights entirely from the frontend, without needing Django admin access.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 KanbanGroup model has a new boolean field can_manage_boards (default False), with migration
- [ ] #2 A helper function user_can_manage_boards(user) in permissions.py returns True for superusers, users with the native aa_kanban.manage_boards permission (backward compatible), or users who are members (direct or via linked Auth Group) of a KanbanGroup with can_manage_boards=True
- [ ] #3 All views currently gated by @permission_required('aa_kanban.manage_boards') (views.py: create_board; views_settings.py: all settings endpoints) are updated to use the new helper via a manage_boards_required decorator
- [ ] #4 Inline has_perm('aa_kanban.manage_boards') checks in views.py (index, board_detail context, edit_board, delete_board ownership fallback) are updated to use user_can_manage_boards
- [ ] #5 Settings UI (group create/edit form) exposes a checkbox to toggle can_manage_boards on a KanbanGroup, fully in the frontend
- [ ] #6 Existing tests updated/passing; new tests cover: KanbanGroup member with can_manage_boards=True can access settings and create/edit/delete boards; member without it cannot
- [ ] #7 CHANGELOG.md updated
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented: KanbanGroup.can_manage_boards field + migration 0023, user_can_manage_boards() helper and manage_boards_required decorator in permissions.py, all 20 manage_boards-gated views in views_settings.py and 3 in views.py migrated. Frontend checkbox added to create/edit group forms and Yes/No badge in group list. 4 new tests added (direct member, via linked Auth Group, denied without flag, settings access). Full suite (105 passed, 8 skipped) verified on devauth sandbox. CHANGELOG.md and plugin AGENTS.md updated.
<!-- SECTION:NOTES:END -->
