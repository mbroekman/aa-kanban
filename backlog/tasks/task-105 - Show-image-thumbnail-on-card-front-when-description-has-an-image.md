---
id: TASK-105
title: Show image thumbnail on card front when description has an image
status: Done
assignee: []
created_date: '2026-10-16 17:28'
updated_date: '2026-10-16 17:28'
labels: []
dependencies: []
ordinal: 119000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Wish: when a card's description contains an image, show a thumbnail preview on the card front in the board/list view, instead of the raw Markdown source text (e.g. '![image.png](/media/...)').
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 A card whose description contains an image shows that image as a thumbnail on the card front
- [x] #2 The text snippet under the thumbnail no longer shows raw image Markdown syntax
- [x] #3 A card with only an image (no other text) shows just the thumbnail, no empty text block
- [x] #4 Unit tests cover multi-image extraction, no-image, dangerous-scheme rejection, and stripping
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Added two pure-function helpers in aa_kanban/markdown.py: extract_first_image_url() (regex-based, rejects unsafe URL schemes via the existing _is_safe_url) and strip_image_markdown() (removes image references, leaving remaining text intact). Exposed as template filters first_image_url / strip_image_markdown in kanban_tags.py. card_item.html now renders a 110px object-fit:cover <img class="kanban-card-thumb"> above the title when present, and only renders the text-snippet block when there is non-empty text left after stripping images. Deliberately regex-based rather than reusing the full render_markdown()+BeautifulSoup pipeline, to avoid a full Markdown parse per card on every board render. 5 new unit tests in test_image_upload.py (TestCardThumbnailExtraction). Verified live on devauth: existing cards with images (Discord test, Image test, Test, test 2) now show real thumbnails instead of raw markdown text; full suite 154 passed/8 skipped.
<!-- SECTION:NOTES:END -->
