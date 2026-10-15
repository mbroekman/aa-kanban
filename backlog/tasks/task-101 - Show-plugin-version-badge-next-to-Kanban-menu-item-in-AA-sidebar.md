---
id: TASK-101
title: Show plugin version badge next to Kanban menu item in AA sidebar
status: Done
assignee: []
created_date: '2026-10-15 09:40'
updated_date: '2026-10-15 09:43'
labels:
  - feature
dependencies: []
ordinal: 115000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Display the installed aa-kanban version (aa_kanban.__version__) as a small muted badge next to the 'Kanban' entry in the Alliance Auth sidebar menu, so admins/users can see which version is deployed at a glance.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Kanban sidebar menu item shows a muted version badge (e.g. v0.14.1) sourced from aa_kanban.__version__
- [x] #2 Menu item hash/text unchanged so no duplicate MenuItem rows are created on upgrade
- [x] #3 Permission check (basic_access) still hides the item entirely
- [x] #4 Unit tests cover badge rendering and permission hiding
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Own BS5 menu template (aa_kanban/menu/menu-item-bs5.html) swapped in inside render() because AA's render_menu overwrites hook.template right before render(). Hook class/text unchanged -> stable MenuItem hash. Verified on devauth via render_menu (badge renders, also inside a folder). 151 passed / 8 skipped.
<!-- SECTION:NOTES:END -->
