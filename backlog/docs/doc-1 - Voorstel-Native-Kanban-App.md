---
id: doc-1
title: Voorstel Native Kanban App
type: specification
created_date: '2026-09-09 20:11'
updated_date: '2026-09-09 20:18'
---
# Voorstel: Native Kanban App voor Alliance Auth (aa-kanban)

## 1. Doel & Scope
Ontwikkelen van een volwaardige, native Kanban applicatie voor Alliance Auth (AA) genaamd `aa-kanban`. De app integreert naadloos in AA met Bootstrap 5, groepsgebaseerd toegangsbeheer (met expliciete scheiding tussen readonly en mutatierechten), en biedt een interactieve drag-and-drop ervaring met behulp van HTMX en SortableJS zonder page reloads.

## 2. Toegangsbeheer & Rechtenstructuur
Borden worden ontsloten middels Alliance Auth `Group`s met twee duidelijke niveaus:
- **Readonly Toegang (`view_groups`)**:
  - Gebruikers in deze groepen kunnen het bord inzien, kolommen en kaarten bekijken en card modals openen om details te lezen.
  - Zij kunnen GEEN kaarten verslepen, aanmaken, bewerken of verwijderen.
- **Mutatie Toegang (`write_groups`)**:
  - Gebruikers in deze groepen kunnen kaarten aanmaken, verslepen tussen kolommen, volgorde wijzigen, beschrijving/assignees bewerken en reacties plaatsen.
- **Superuser Access**:
  - Superusers hebben altijd volledige lees- en mutatietoegang tot alle borden.
- **Algemene App Permissies**:
  - `basic_access`: Toegang om de app in AA te openen en toegewezen borden te zien.
  - `manage_boards`: Beheerdersrechten om borden aan te maken, te configureren en groepen toe te wijzen.

## 3. Datamodellen & Architectuur
De datamodellen in `models.py` van `aa_kanban`:
- **Board**:
  - `name`: CharField(max_length=255)
  - `slug`: SlugField(unique=True)
  - `description`: TextField(blank=True)
  - `view_groups`: ManyToManyField(Group, blank=True, related_name="kanban_view_boards")
  - `write_groups`: ManyToManyField(Group, blank=True, related_name="kanban_write_boards")
  - `created_by`: ForeignKey(User, on_delete=SET_NULL, null=True, related_name="+")
  - `created_at` & `updated_at`: DateTimeFields
  - Methoden: `can_user_view(user)`, `can_user_write(user)`
- **List (Kolom)**:
  - `board`: ForeignKey(Board, on_delete=CASCADE, related_name="lists")
  - `name`: CharField(max_length=100)
  - `order`: PositiveIntegerField(default=0)
  - `created_at` & `updated_at`: DateTimeFields
  - Meta: `ordering = ["order", "id"]`
- **Card (Taak)**:
  - `list`: ForeignKey(List, on_delete=CASCADE, related_name="cards")
  - `title`: CharField(max_length=255)
  - `description`: TextField(blank=True)
  - `order`: PositiveIntegerField(default=0)
  - `assignees`: ManyToManyField(User, blank=True, related_name="assigned_kanban_cards")
  - `due_date`: DateTimeField(null=True, blank=True)
  - `created_by`: ForeignKey(User, on_delete=SET_NULL, null=True, related_name="+")
  - `created_at` & `updated_at`: DateTimeFields
  - Meta: `ordering = ["order", "id"]`
- **Label & Comment (V1 ondersteuning)**:
  - `Label`: name, color, board FK
  - `Comment`: card FK, author FK, text, created_at

## 4. Frontend & Drag-and-Drop (HTMX + SortableJS)
- **Templates**: Bootstrap 5 syntax conform AA v5 (`data-bs-*`).
- **Drag & Drop**:
  - SortableJS wordt alleen geactiveerd als `can_user_write` waar is.
  - Readonly gebruikers zien de kaarten zonder drag-handles en interactieve sleep-functies.
  - Bij `onEnd`: HTMX POST naar `/cards/<id>/move/` met nieuwe lijst en index volgorde.
  - Backend controleert `board.can_user_write(request.user)` en voert update uit in `transaction.atomic()`.
- **Modals**:
  - Bootstrap 5 modal geladen via HTMX (`hx-get`) voor kaartdetails. Edit-opties zijn alleen zichtbaar voor gebruikers met mutatierechten.

## 5. Test- & Kwaliteitsstrategie
- Opzetten van `testauth` harness voor `pytest-django`.
- Unittests voor modellen, readonly vs write permissies, cascades, drag & drop API endpoints.
- Preventie van N+1 queries via `select_related` en `prefetch_related`.
- Strikte typing en linting met `mypy` en `ruff`.

## 6. Backlog Taken
- TASK-1: Ontwikkeling Native Kanban App voor Alliance Auth (Epic)
  - TASK-1.7: Project hernoemen naar aa-kanban [Done]
  - TASK-1.1: Test-harness en environment inrichten [To Do]
  - TASK-1.2: Datamodellen implementeren en unit tests schrijven [To Do]
  - TASK-1.3: URL Routing, Auth Hooks en Permissies implementeren [To Do]
  - TASK-1.4: Basis Views en Bootstrap 5 Templates bouwen [To Do]
  - TASK-1.5: HTMX en SortableJS Drag & Drop integratie [To Do]
  - TASK-1.6: Card Detail Modal, Assignees en Comments [To Do]
