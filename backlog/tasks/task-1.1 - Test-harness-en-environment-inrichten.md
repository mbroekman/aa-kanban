---
id: TASK-1.1
title: Test-harness en environment inrichten
status: Done
assignee:
  - '@antigravity'
created_date: '2026-09-09 20:10'
updated_date: '2026-09-09 20:25'
labels: []
dependencies:
  - TASK-1.7
parent_task_id: TASK-1
priority: high
type: task
ordinal: 2000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Inrichten van testauth en pytest configuratie zodat pytest-django en unit tests probleemloos lokaal draaien.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 testauth configuratie aanwezig voor pytest
- [x] #2 pytest draait succesvol via .venv/bin/pytest
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Testauth structuur ingericht met testauth/settings/local.py (gekoppeld aan PACKAGE = 'aa_kanban'), urls.py en sqlite configuratie. Pytest-django, pytest-cov en factory_boy geïnstalleerd in .venv. Smoke tests toegevoegd in aa_kanban/tests/test_smoke.py. Verificatie uitgevoerd: 2/2 tests geslaagd en ruff check 100% clean.
<!-- SECTION:NOTES:END -->

## Final Summary

<!-- SECTION:FINAL_SUMMARY:BEGIN -->
Testauth harness en pytest omgeving succesvol ingericht. Pytest suite draait en verifieert app installatie en database access.
<!-- SECTION:FINAL_SUMMARY:END -->
