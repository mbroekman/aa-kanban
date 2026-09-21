---
id: TASK-2
title: 'Bug: Toevoegen van een board geeft een spinning icon'
status: Done
assignee: []
created_date: '2026-09-21 06:59'
updated_date: '2026-09-21 07:28'
labels: []
dependencies: []
type: bug
ordinal: 10000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Wanneer een gebruiker een nieuw board probeert aan te maken, blijft er een spinning icon zichtbaar. Waarschijnlijk een HTMX/backend communicatie probleem.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Board kan succesvol worden toegevoegd via UI
- [x] #2 Geen oneindige spinning icon bij succes of validatiefout
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Oorzaak gevonden: htmx.min.js werd helemaal niet ingeladen op index.html, waardoor de hx-get op de 'New Board' knop genegeerd werd. De modal opende wel, maar bleef steken op het standaard laad-icoontje omdat het formulier nooit werd opgehaald. Dit is opgelost door htmx.min.js centraal in base.html te plaatsen (in blok extra_javascript). Tests slagen.
<!-- SECTION:NOTES:END -->
