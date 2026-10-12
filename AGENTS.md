# AA-Kanban - AI Agent Guidelines

Dit project maakt integraal onderdeel uit van de Workbench 001 workspace en erft alle bindende richtlijnen van het centrale hoofd-instructiedocument:
👉 **\[Centrale AGENTS.md\](file:///g:/My%20Drive/Workbench%20001/AGENTS.md)**

Lees tevens altijd eerst \[.agent/memory.md\](file:///g:/My%20Drive/Workbench%20001/.agent/memory.md) vóór analyse of modificatie (Regel 1 van AGENTS.md).

______________________________________________________________________

## 1. Project Context & Backlog Directory

- **Plugin:** `aa-kanban` (Django App: `aa_kanban`)
- **Backlog Map:** `plugins/aa-kanban/backlog/`
- **Directory Context (CRITICAL):** Alle `backlog` CLI commando's en MCP interacties **MOETEN** worden uitgevoerd met de werkmap ingesteld op `plugins/aa-kanban` (bijv. `cd plugins/aa-kanban` of via de `Cwd` parameter in toolcalls), zodat taken correct in de backlog van `aa-kanban` worden geplaatst en beheerd.

______________________________________________________________________

## 2. Bindende Centrale Regels (Inherited from Master AGENTS.md)

Alle standaarden uit de centrale \[AGENTS.md\](file:///g:/My%20Drive/Workbench%20001/AGENTS.md) zijn hier onverkort van toepassing:

- **Taakbeheer via Backlog.md:** Eerst taak registreren/WIP zetten in `backlog-md` vóór het schrijven of wijzigen van code. Alle taken (titels, beschrijvingen, acceptatiecriteria en notities) **MOETEN in het Engels** zijn. Afronden pas na testen, linting en type-checks.
- **Tooling & Omgeving:** `uv` voor package management, `Ruff` (line-length 120), `mypy` strict met `django-stubs`, `pytest` en `pytest-django`.
- **Alliance Auth UI & Bootstrap 5:** Altijd `{% extends "allianceauth/base-bs5.html" %}`, uitsluitend Bootstrap 5 componenten (`card`, `badge bg-*`, `d-flex`, `btn-sm`). Nooit Bootstrap 3 componenten (`panel`, `label`, `pull-right`). Geen eigen `{% if messages %}` block toevoegen.
- **Pre-Commit Verificatie:** Update `CHANGELOG.md` en user docs vóór taakafronding. Nooit automatische releases of tags.

______________________________________________________________________

## 3. Project-Specifieke Conventies (AA-Kanban)

### Alliance Auth v5 & Bootstrap 5 Modals

- Gebruik **altijd** Bootstrap 5 syntax (`data-bs-toggle`, `data-bs-target`, `data-bs-dismiss`) voor modals en interactieve elementen. Nooit verouderde Bootstrap 3/4 tags.
- Modals geopend via HTMX dienen een volwaardige Bootstrap 5 modal structuur te hebben en te luisteren naar het globale `closeModal` event.

### Board Management Toegang (Frontend, niet Admin)

- Beheer van boards (settings-pagina, boards aanmaken/bewerken/verwijderen) wordt bepaald door `user_can_manage_boards()` in `permissions.py`, **niet** rechtstreeks door `has_perm("aa_kanban.manage_boards")`.
- Toekenning hoort primair via `KanbanGroup.can_manage_boards` (frontend Settings-UI, direct lidmaatschap of via gekoppelde Auth Group) te lopen, conform ADR-006 (functionele config in frontend, Django `/admin/` alleen technisch). De native `aa_kanban.manage_boards` permissie blijft als backward-compatible fallback werken.
- Gebruik voor nieuwe board-beheer views altijd de decorator `@manage_boards_required` (niet `@permission_required("aa_kanban.manage_boards")`).

### Discord Notificaties & Teams

- `KanbanTeam` ondersteunt gekoppelde Django Auth Groups (`groups`). Gebruik `team.get_all_members()` om zowel directe teamleden als groepsleden op te halen voor notificaties en thread invites.
- Stale card alerts (`stale_card_alert_hours`) controleren zowel card edits als card comments als activiteit en sluiten voltooide kolommen ('Done'/'Afgerond') automatisch uit.
