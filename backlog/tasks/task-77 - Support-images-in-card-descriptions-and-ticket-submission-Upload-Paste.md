---
id: TASK-77
title: Support images in card descriptions and ticket submission (Upload & Paste)
status: To Do
assignee: []
created_date: '2026-10-11 21:03'
updated_date: '2026-10-12 07:10'
labels: []
dependencies: []
ordinal: 93000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Add support for images via file upload, drag-and-drop, and clipboard paste (Ctrl+V) in card descriptions and ticket submission forms. Secure storage in MEDIA_ROOT and inline Markdown rendering.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Backend image upload endpoint with MIME and size validation storing in MEDIA_ROOT
- [ ] #2 Clipboard paste (Ctrl+V), drag-and-drop, and file upload picker in card description textarea
- [ ] #3 Clipboard paste (Ctrl+V), drag-and-drop, and file upload picker in ticket submission form textarea
- [ ] #4 Safe Markdown rendering with inline images and zoom/lightbox preview in card modal
- [ ] #5 Unit tests verifying image upload endpoint, permissions, and validation
<!-- AC:END -->
