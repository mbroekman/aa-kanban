---
id: TASK-123
title: Switch card description back to Preview tab on Save Changes
status: Done
assignee: []
created_date: '2026-11-25 15:04'
updated_date: '2026-11-25 15:05'
labels: []
dependencies: []
ordinal: 508000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Control the description Preview/Edit tab in CardDetailDialog so Save Changes automatically switches back to Preview and disables saving while an image upload is in flight.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Save Changes switches description tab back to Preview and shows a brief Saved indicator
- [x] #2 Save Changes is disabled while uploadingImage is true
- [x] #3 Frontend build passes and is deployed
<!-- AC:END -->
