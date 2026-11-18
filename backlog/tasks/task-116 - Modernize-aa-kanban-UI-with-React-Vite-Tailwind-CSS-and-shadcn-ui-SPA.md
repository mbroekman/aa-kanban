---
id: TASK-116
title: 'Modernize aa-kanban UI with React, Vite, Tailwind CSS, and shadcn/ui SPA'
status: Done
assignee: []
created_date: '2026-11-18 11:11'
updated_date: '2026-11-18 11:38'
labels: []
dependencies: []
ordinal: 130000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Build a modern SPA proof of concept for aa-kanban using React, TypeScript, Vite, Tailwind CSS (scoped without preflight to coexist with Alliance Auth Bootstrap 5), and shadcn/ui components, backed by JSON API endpoints.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [x] #1 Vite + React + TypeScript + Tailwind + shadcn/ui frontend builds cleanly into aa_kanban/static/aa_kanban/spa/
- [x] #2 JSON API endpoints serve board overview, board detail (lists, cards, labels, teams, assignees), and card CRUD/move/comments
- [x] #3 SPA mounts inside allianceauth/base-bs5.html without CSS conflicts with Bootstrap 5 / Darkly
- [x] #4 Existing pytest suite passes plus new tests for JSON API endpoints
<!-- AC:END -->
