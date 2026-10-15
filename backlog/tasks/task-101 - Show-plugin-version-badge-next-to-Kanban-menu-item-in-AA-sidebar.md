---
id: TASK-101
title: Show app name and version badge in AA header (header_nav_brand)
status: Done
assignee: []
created_date: '2026-10-15 09:40'
updated_date: '2026-10-15 10:45'
labels:
  - feature
dependencies: []
ordinal: 115000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Follow the aa-industry pattern: fill the header_nav_brand block in aa_kanban/base.html with the configured app name (AA_KANBAN_APP_NAME, same as the sidebar menu) plus a version badge (aa_kanban.__version__), instead of the generic site name. Initial sidebar-badge implementation (6df3e21) was not what the user meant and is reverted.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 AA top header on all aa-kanban pages shows the app name from AA_KANBAN_APP_NAME (same as the sidebar menu) instead of the site name
- [x] #2 A version badge (v + aa_kanban.__version__) is shown next to the header name, styled like aa-industry
- [x] #3 Sidebar menu item is unchanged (sidebar badge from 6df3e21 reverted)
- [x] #4 Unit tests cover the header brand name and version badge
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Reverted sidebar menu badge. Implemented aa-industry pattern: header_nav_brand block in aa_kanban/base.html rendering kanban_app_name and kanban_version badge (styled with badge bg-secondary ms-2 text-white). Verified on devauth live rendering where header displays 'Project Management v0.14.1'. All 149 tests pass on remote devauth.
<!-- SECTION:NOTES:END -->
