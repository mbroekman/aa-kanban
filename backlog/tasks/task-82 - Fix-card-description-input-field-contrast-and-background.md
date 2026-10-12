---
id: TASK-82
title: Fix card description input field contrast and background
status: Done
priority: high
created: 2026-10-12
assigned_to: Antigravity
labels:
  - bug
  - ui
  - bootstrap5
  - contrast
---

## Description
In TASK-77, image uploads and markdown previews were introduced. However, the card description `<textarea>` and ticket form `<textarea>` were styled with `border-0 bg-transparent shadow-none` inside a low-opacity wrapper (`rgba(255, 255, 255, 0.04)`). In dark Bootswatch themes (e.g. Darkly), the input field blends into the modal background without visible borders or distinction, making entered text difficult to see.

## Acceptance Criteria
- [x] Restore standard Bootstrap 5 `.form-control` appearance on the description `<textarea>` in `card_modal_content.html` so it has distinct input background, crisp borders, and high-contrast text matching other form fields (e.g. comment textarea).
- [x] Restore standard Bootstrap 5 `.form-control` appearance on the ticket description `<textarea>` in `ticket_form.html`.
- [x] Maintain drag-and-drop file upload, `[Attach Image]` button, and `Ctrl+V` paste functionality seamlessly on the enhanced form control.
- [x] Update `kanban.css` dragover styling so that dragover highlights the input border/focus state clearly without obscuring input text.
- [x] Verify unit tests pass and sync changes to `devauth.spral.space`.
