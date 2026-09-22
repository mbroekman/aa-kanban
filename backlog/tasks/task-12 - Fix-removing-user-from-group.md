---
id: TASK-12
title: Fix removing user from group
status: Done
assignee: []
created_date: '2026-09-22 12:07'
updated_date: '2026-09-22 12:09'
labels: []
dependencies: []
ordinal: 20000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Removing a user from the group by clicking the cross (X) in the user management modal doesn't work.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Clicking the cross removes the user from the group; Modal and background group list update correctly
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added missing hx-headers='{"X-CSRFToken": "{{ csrf_token }}"}' to the remove user button in group_users_modal.html and the delete group button in group_list.html. Without this header, HTMX POST requests not enclosed in a form fail Django's CSRF validation with a 403 Forbidden error.
<!-- SECTION:NOTES:END -->
