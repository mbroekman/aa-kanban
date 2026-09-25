---
id: TASK-17
title: Implement Kanban Feedback
status: Done
assignee: []
created_date: '2026-09-25 10:37'
updated_date: '2026-09-25 10:43'
labels: []
dependencies: []
type: feature
ordinal: 25000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Implement user feedback: 1. Default column configs (Backlog, To Do, In Progress, Review/Testing, Done) 2. Global labels across boards 3. Summary view of all boards 4/5. Discord ticket integration for Kanban with member creation
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Default column config added
- [ ] #2 Labels pooled globally
- [ ] #3 Summary view implemented
- [ ] #4 Discord ticket system integrated
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
1. Default columns configured to be created alongside new Boards.
2. Label board ForeignKey removed, labels are now pooled globally.
3. Added Summary View page accessible from Kanban Boards index.
4/5. Added Submit Ticket view allowing members to create a card acting as a ticket on a configured board (set in Settings), complete with labels.
<!-- SECTION:NOTES:END -->
