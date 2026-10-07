---
id: TASK-70
title: Fix hardcoded Dutch strings and enforce i18n
status: Done
assignee: []
created_date: '2026-10-02 14:34'
updated_date: '2026-10-02 14:41'
labels: []
dependencies: []
ordinal: 86000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
There are hardcoded Dutch texts appearing in the UI (e.g. error message on ticket creation) when the language is set to English. Ensure all strings use proper gettext _() translation wrappers and English is the base language.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Error message when creating a ticket is properly translated using _()
- [x] #2 No hardcoded Dutch strings remain in Python files
- [x] #3 No hardcoded Dutch strings remain in HTML templates
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Replaced all hardcoded Dutch strings in views.py (including the ticket creation error messages) with English base strings wrapped in gettext_lazy `_()`. Checked templates and confirmed they are using `{% trans %}` correctly. Appended the missing Dutch translations to `django.po` and compiled them to `django.mo`.
<!-- SECTION:NOTES:END -->
