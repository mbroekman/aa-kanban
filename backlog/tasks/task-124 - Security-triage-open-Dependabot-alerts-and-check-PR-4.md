---
id: TASK-124
title: Security triage open Dependabot alerts, and check PR #4 is still valid
status: To Do
assignee: []
created_date: '2026-11-27 09:30'
labels: []
dependencies: []
ordinal: 124000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
2 open Dependabot alerts (2026-11-27): dnspython (#15), soupsieve (#12). Compare
against the aa-kanban TASK-86 precedent (ecdsa/python-jose: `tolerable_risk`,
no upstream fix) before deciding whether these two need a `uv.lock` bump or the
same dismissal.

Also check whether **Dependabot PR #4** ("bump the uv group... with 2 updates",
uv.lock only) is still valid before merging: confirmed 2026-11-27 it is -
`mergeable: true`, `mergeable_state: clean`, no conflicts with current `main`.
<!-- SECTION:DESCRIPTION:END -->
