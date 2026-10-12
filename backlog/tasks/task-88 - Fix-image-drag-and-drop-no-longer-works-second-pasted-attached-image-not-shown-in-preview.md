---
id: TASK-88
title: >-
  Fix: image drag-and-drop no longer works, second pasted/attached image not
  shown in preview
status: Done
assignee: []
created_date: '2026-10-12 18:41'
updated_date: '2026-10-12 18:51'
labels: []
dependencies: []
ordinal: 102000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Two regressions reported after TASK-87's fixes: (1) dragging and dropping an image file onto the card description editor no longer uploads/inserts it; (2) when a second image is added (via paste/drag-drop/attach) to a description that already has one image, the second image does not appear in the rendered preview. Need to reproduce live in the browser on devauth and trace the exact failure in kanban.js's initMarkdownImageUploads/drag-drop handlers and the markdown rendering path.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Drag-and-drop of an image file onto the card/ticket description editor uploads it and inserts the markdown reference, matching paste and Attach Image behavior
- [ ] #2 Adding a second image to a description (any method) renders both images correctly in the preview/view mode
- [ ] #3 Regression test(s) added where feasible
- [ ] #4 Full test suite green on devauth sandbox
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
ROOT CAUSE: kanban.js's entire DOMContentLoaded handler returned early via 'if (!boardContainer) return;' on any page lacking .kanban-board-container -- which includes the standalone ticket submission form. This meant initMarkdownImageUploads() (paste/drag-drop/Attach Image binding) NEVER ran there, since this guard predates TASK-77 (present since the very first kanban.js commit). Confirmed live via Chrome: window.toggleCardDescMode was literally undefined on the ticket form page, and the Attach Image button had no bound click handler. This explains BOTH reported symptoms with one cause: drag-and-drop silently did nothing (no listener attached), and a 'second image' never showed in the preview because it was never actually inserted into the textarea in the first place. FIX: restructured kanban.js so only the board-specific SortableJS column drag-and-drop logic stays gated behind boardContainer; image upload init and the rest of the script (toggleCardDescMode, htmx listeners, etc.) now run unconditionally on every page with a markdown editor. Live-verified on devauth via synthetic File drop events: two images now upload correctly via drag-and-drop on the ticket form and both render in the live AJAX preview. Card modal / board page behavior unaffected (confirmed via console + function existence checks, 107 passed 8 skipped).
<!-- SECTION:NOTES:END -->
