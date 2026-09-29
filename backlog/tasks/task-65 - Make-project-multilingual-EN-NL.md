---
id: TASK-65
title: Make project multilingual (EN/NL)
status: Done
assignee:
  - '@antigravity'
created_date: '2026-09-29 11:06'
updated_date: '2026-09-29 13:16'
labels: []
dependencies: []
ordinal: 81000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->

The project needs to support both English and Dutch. Currently, some parts may be hardcoded or missing translations.

<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->

- [ ] #1 Django translation mechanism (gettext) is set up
- [ ] #2 All user-facing strings are marked for translation
- [ ] #3 English and Dutch translations are provided and compile successfully
- [ ] #4 1,2

<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->

1. Wrap Python strings with gettext_lazy. 2. Wrap template strings with trans/blocktrans. 3. Add locale dir and run makemessages for en and nl. 4. Translate .po files. 5. Compilemessages.

<!-- SECTION:PLAN:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->

Implemented translations using gettext and compiled nl and en locales. Fixed all pre-commit formatting issues.

<!-- SECTION:NOTES:END -->
