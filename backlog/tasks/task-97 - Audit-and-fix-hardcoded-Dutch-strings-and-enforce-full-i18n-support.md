---
id: TASK-97
title: Audit and fix hardcoded Dutch strings and enforce full i18n support
status: Done
assignee: []
created_date: '2026-10-14 08:44'
labels: []
dependencies: []
priority: medium
type: bug
ordinal: 111000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Audit all Python code, templates, and JavaScript in aa-kanban for hardcoded Dutch strings (such as 'Bekijk Bord' and webhook notifications) and missing gettext/trans tags. Enforce English as standard base language and update Dutch translations in locale/nl/LC_MESSAGES/django.po and django.mo.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Find and replace all hardcoded Dutch strings with standard English wrapped in gettext
- [x] #2 Verify all template strings use trans or blocktrans tags
- [x] #3 Update locale/nl/LC_MESSAGES/django.po and compilemessages to django.mo
- [x] #4 Add or update unit tests to verify bilingual string translations
- [x] #5 Ensure all tests pass on devauth sandbox
<!-- AC:END -->
