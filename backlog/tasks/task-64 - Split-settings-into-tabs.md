---
id: TASK-64
title: Split settings into tabs
status: Done
assignee:
  - '@antigravity'
created_date: '2026-09-29 08:05'
updated_date: '2026-09-29 08:12'
labels: []
dependencies: []
type: enhancement
ordinal: 80000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Organize the settings page into Tabs for Groups, Teams, and Labels to make it cleaner.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Settings page uses Bootstrap tabs
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Implemented Bootstrap 5 tabs in settings.html to separate Groups, Teams, and Labels for a cleaner layout.

Fixed a bug where HTML closing div tags were breaking out of the tab-content block, causing subsequent tabs to render incorrectly with empty spaces.
<!-- SECTION:NOTES:END -->
