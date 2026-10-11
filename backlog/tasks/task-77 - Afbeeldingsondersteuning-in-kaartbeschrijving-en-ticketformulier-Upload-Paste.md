---
id: TASK-77
title: >-
  Afbeeldingsondersteuning in kaartbeschrijving en ticketformulier (Upload &
  Paste)
status: To Do
assignee: []
created_date: '2026-10-11 21:03'
labels: []
dependencies: []
ordinal: 93000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Ondersteuning toevoegen voor het toevoegen van afbeeldingen via upload, drag-and-drop en clipboard paste (Ctrl+V) in kaartbeschrijvingen en bij het aanmaken van nieuwe tickets. Veilige opslag in MEDIA_ROOT en inline Markdown-rendering.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Backend upload endpoint voor afbeeldingen met MIME/size validatie en opslag in MEDIA_ROOT
- [ ] #2 Clipboard paste (Ctrl+V), drag-and-drop en file upload picker in kaartbeschrijving textarea
- [ ] #3 Clipboard paste (Ctrl+V), drag-and-drop en file upload picker in ticketformulier textarea
- [ ] #4 Veilige Markdown rendering met inline weergave en lightbox/zoom voor afbeeldingen in de kaart modal
- [ ] #5 Unit tests voor image upload endpoint en validatie
<!-- AC:END -->
