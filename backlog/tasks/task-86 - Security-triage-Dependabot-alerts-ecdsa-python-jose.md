---
id: TASK-86
title: 'Security: triage Dependabot alerts (ecdsa, python-jose)'
status: Done
assignee: []
created_date: '2026-10-12 16:53'
labels: []
dependencies: []
ordinal: 100000
---

## Description

<!-- SECTION:DESCRIPTION:BEGIN -->
Investigated 2 Dependabot alerts (1 critical: python-jose GHSA-3qf3-8w2g-rqmx / CVE-2026-85394; 1 high: ecdsa GHSA-wj6h-64fc-37mp / CVE-2024-23342). Both are transitive dependencies pulled in via allianceauth -> django-esi (used for EVE SSO JWT validation), not direct choices of aa-kanban. Neither has a patched version available: the ecdsa maintainer explicitly declined to fix the Minerva timing attack (pure-Python cannot be constant-time); python-jose 3.5.0 (latest) still has an incomplete fix for the algorithm-confusion issue. Since no version bump can resolve either and aa-kanban never calls python-jose/ecdsa directly, both alerts were dismissed on GitHub with reason 'tolerable_risk' and a documented explanation. Re-visit if django-esi ever migrates away from python-jose/ecdsa, or if upstream ships a fix.
<!-- SECTION:DESCRIPTION:END -->

## Acceptance Criteria
<!-- AC:BEGIN -->
- [ ] #1 Both Dependabot alerts dismissed on GitHub with documented reasoning
- [ ] #2 Finding recorded in workspace memory.md for future sessions
<!-- AC:END -->

## Implementation Notes

<!-- SECTION:NOTES:BEGIN -->
Resolved by dismissal (no code fix exists). See CHANGELOG not needed (no behavior change). Alerts: https://github.com/mbroekman/aa-kanban/security/dependabot/1 and /2
<!-- SECTION:NOTES:END -->
