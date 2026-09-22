---
id: TASK-9
title: Refresh group member list on modal close
status: Done
assignee: []
created_date: '2026-09-22 11:30'
updated_date: '2026-09-22 11:32'
labels: []
dependencies: []
ordinal: 17000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
When a user adds a user to a group and closes the dialog, the underlying page is not refreshed so the new member is not visible. Fix this so the member list is updated/the page is refreshed.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Underlying page refreshes or updates when edit group modal is closed; New member is visible in the list
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added an HTMX out-of-band (hx-swap-oob) update to group_users_modal.html when a user is added or removed. The views_settings.py was updated to pass the full 'groups' context to the modal so that the group_list.html partial can be correctly rendered and swapped into the background page while the modal is still open, meaning the underlying member list is always up-to-date even before closing the modal.
<!-- SECTION:NOTES:END -->
