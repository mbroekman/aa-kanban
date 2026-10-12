---
id: TASK-77
title: Support images in card descriptions and ticket submission (Upload & Paste)
status: Done
assignee: []
created_date: '2026-10-11 21:03'
updated_date: '2026-10-12 08:35'
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
- [x] #1 Backend image upload endpoint with MIME and size validation storing in MEDIA_ROOT
- [x] #2 Clipboard paste (Ctrl+V), drag-and-drop, and file upload picker in card description textarea
- [x] #3 Clipboard paste (Ctrl+V), drag-and-drop, and file upload picker in ticket submission form textarea
- [x] #4 Safe Markdown rendering with inline images and zoom/lightbox preview in card modal
- [x] #5 Unit tests verifying image upload endpoint, permissions, and validation
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
- Implemented `upload_image` endpoint (`/kanban/api/upload-image/`) validating user permissions, 5MB max size, file extensions (.png, .jpg, .jpeg, .gif, .webp), and initial magic bytes.
- Created `KanbanAttachment` model and migration `0022_kanbanattachment` to track image attachments securely in `MEDIA_ROOT`.
- Created `aa_kanban.markdown` engine utilizing `markdown` and `BeautifulSoup4` for strict XSS sanitization (disallowing scripts, iframes, onerror, javascript URLs) and styling responsive inline images (`img-fluid rounded kanban-rendered-image`).
- Added global Bootstrap 5 Lightbox zoom modal (`#kanbanImageLightboxModal`) in `base.html` with click listener for instant fullscreen image view.
- Added `/kanban/api/preview-markdown/` endpoint, live `[Write]` / `[Preview]` tabs in `ticket_form.html`, and edit toggle in `card_modal_content.html`.
- Added clipboard paste (`Ctrl+V`), drag-and-drop dropzone, and file picker button (`[Attach Image]`) in `kanban.js`.
- Added comprehensive unit test suite in `aa_kanban/tests/test_image_upload.py`.
<!-- SECTION:NOTES:END -->
