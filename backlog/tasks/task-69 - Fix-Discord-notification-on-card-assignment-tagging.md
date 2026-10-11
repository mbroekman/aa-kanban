---
id: TASK-69
title: Fix Discord notification on card assignment/tagging
status: Done
assignee: []
created_date: '2026-10-02 14:11'
updated_date: '2026-10-02 14:11'
labels: []
dependencies: []
ordinal: 85000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

Discord notifications are not being sent when a user is assigned or tagged in a Kanban card.

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->

- [x] #1 Assigning/tagging a user triggers a Discord DM to that user

<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->

The Discord DM notification on card assignment was failing silently (or causing a 500 error in the background) because the message was generated using `gettext_lazy` as `_`. This creates a lazy translation object (a Promise). When passed directly to Celery's `.delay()` method, it fails to serialize to JSON. I added `str(msg)` inside `views_api.py` to eagerly evaluate and convert the lazy translation object into a string before passing it to Celery. This ensures the Celery task receives a serializable string and the Discord DM is properly sent on assignment.

<!-- SECTION:NOTES:END -->
