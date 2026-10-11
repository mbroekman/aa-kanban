---
id: TASK-75
title: Fix pre-commit check failures on GitHub Actions
status: Done
assignee:
  - '@antigravity'
created_date: '2026-10-11 17:23'
updated_date: '2026-10-11 17:38'
labels:
  - ci
  - pre-commit
dependencies: []
ordinal: 91000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Onderzoek en herstel de fouten in de pre-commit workflow op GitHub Actions (run https://github.com/mbroekman/aa-kanban/actions/runs/38062511092/job/114243471449#step:4:1091).
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria

<!-- AC:BEGIN -->
- [x] #1 Oorzaak van de pre-commit check faalactie geïdentificeerd
- [x] #2 Relevante bestanden/configuraties gecorrigeerd conform pre-commit regels
- [x] #3 Alle pre-commit checks slagen lokaal / in remote sandbox
- [x] #4 Wijzigingen gedocumenteerd in CHANGELOG.md en gepusht
<!-- AC:END -->

## Implementation Plan

<!-- SECTION:PLAN:BEGIN -->
1. Haal de exacte foutmelding op uit de GitHub Actions run of reproduceer lokaal/via remote pre-commit runner.
2. Pas de vereiste fixes toe op de code en/of configuratie.
3. Valideer met pre-commit run --all-files.
4. Werk documentatie en backlog bij.
<!-- SECTION:PLAN:END -->
