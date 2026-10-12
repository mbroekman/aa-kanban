---
id: TASK-78
title: Fix hardcoded Dutch strings in stale card alerts (i18n & Celery translation)
status: Done
assignee: []
created_date: '2026-10-11 21:04'
updated_date: '2026-10-12 07:12'
labels: []
dependencies: []
ordinal: 94000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Stale card alert notifications are sent in Dutch instead of English when English is the selected language. Ensure notification messages are standardly in English (conforming to AA standards) and translated via gettext/i18n to respect the configured user/board language.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Stale card alert message strings in tasks.py are standardly in English
- [x] #2 Translatable strings with gettext / translation correctly handled in Celery task
- [x] #3 Unit tests verify English output of stale card alerts and language switching
<!-- AC:END -->
