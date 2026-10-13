---
id: TASK-92
title: Allow editing global labels in frontend settings
status: Done
assignee: []
created_date: '2026-10-13 08:01'
updated_date: '2026-10-13 08:09'
labels: []
dependencies: []
priority: medium
type: enhancement
ordinal: 106000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Users can currently create and delete global labels under /kanban/settings/#labels, but cannot edit existing labels. Add an Edit Label modal allowing users with board management permissions to update label name and color.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Add Edit button and edit modal to labels list in frontend settings
- [x] #2 Implement backend view and URL endpoint to handle label editing with name and color validation
- [x] #3 Ensure proper permission checks using user_can_manage_boards / manage_boards_required
- [x] #4 Add unit tests for label editing and permissions
- [x] #5 Verify complete test suite passes
<!-- AC:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Added Edit Label button and modal to /kanban/settings/#labels, implemented edit_settings_label view and URL endpoint, protected with manage_boards_required, added unit tests (114 passing), live verified in sandbox with screenshot capture, and updated user manuals and CHANGELOG.
<!-- SECTION:FINAL_SUMMARY:END -->
