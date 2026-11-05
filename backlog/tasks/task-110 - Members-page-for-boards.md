---
id: TASK-110
title: Members page for boards
status: Done
assignee: []
created_date: '2026-11-05 09:51'
updated_date: '2026-11-05 09:54'
labels:
  - feature
dependencies: []
ordinal: 124000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
A board can be marked as a Members Board. Such boards leave the management dashboard and appear on a separate members page with its own Auth menu item. Everyone with Kanban basic access can view them; only the board's write groups can change them. The menu name is set in the Kanban settings (General tab).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Members Board checkbox on board create and edit
- [x] #2 Members boards appear only on the members page, not on the dashboard or summary
- [x] #3 Everyone with basic_access can view a members board; writing still needs a write group
- [x] #4 Auth menu item for the members page, shown only when a members board exists, named by KanbanSetting.members_page_name editable in Settings > General
- [x] #5 Tests cover visibility, write access, the menu name and the settings form
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Shipped in 81c3cc5 with migration 0027. Verified on devauth (migrated, restarted): dashboard, members page, archived boards, settings and summary return 200; in a rolled-back transaction a members board showed in the menu and on the members page, and archiving moved it to Archived Boards with a Restore button on the board.
<!-- SECTION:NOTES:END -->
