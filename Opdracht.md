# Opdracht: Ontwikkel een native Kanban (Trello-like) App voor Alliance Auth

## Context

Ontwikkel een custom Django-app voor Alliance Auth (AA) genaamd `aa-kanban`. Deze app levert een volledige Kanban-functionaliteit binnen de AA-omgeving, vergelijkbaar met Trello. De code moet strikt voldoen aan de Alliance Auth developer guidelines en onze `.cursorrules`.

## Core Features & Datamodellen

De applicatie vereist minimaal de volgende relationele structuur:

1. **Board:** Heeft een naam, beschrijving, en is gekoppeld aan specifieke Alliance Auth `Group`s voor toegangsbeheer (bijv. alleen toegankelijk voor directors of een specifieke SIG).
2. **List (Kolom):** Gekoppeld aan een Board. Heeft een naam en een volgorde-integer (`order`).
3. **Card (Taak):** Gekoppeld aan een List. Heeft een titel, beschrijving, aanmaakdatum en een volgorde-integer.
4. **Card Assignees:** Mogelijkheid om Alliance Auth `User` objecten toe te wijzen aan een Card.
5. **Comments & Labels (Optioneel voor V1):** Gebruikers moeten reacties kunnen plaatsen op Cards en kleur-labels kunnen toewijzen.

## UI & Frontend Stack

* **Styling:** Gebruik de standaard Alliance Auth Bootstrap 3/5 thema's zodat de app naadloos integreert in de rest van de portal.
* **Interactiviteit (Drag & Drop):** Gebruik **HTMX** en **SortableJS** in de Django templates om Cards tussen Lists te slepen zonder page reloads, en waarbij de backend asynchroon wordt geüpdatet.
* **Views:**
  * Een overzichtspagina met alle toegankelijke Boards voor de ingelogde gebruiker.
  * De detailpagina van het Board met het Kanban-bord.
  * Een modale pop-up (Bootstrap Modal via HTMX) voor de Card-details (beschrijving, toewijzingen).

## Alliance Auth Integratie

* **Permissies:** Gebruik de `@permission_required` decorators van Django/AA. Alleen gebruikers met specifieke AA-groepsrechten mogen bepaalde borden zien of bewerken.
* **Navigatie:** Zorg voor een correcte integratie in het AA-menu via `auth_hooks.py`.

## Executie Protocol

1. **[MANDATORY]** Start de `backlog-md` tool.
2. Breek dit project op in logische stappen: Datamodellen, URL routing, Auth Hooks, Basis Views, HTMX Drag&Drop integratie.
3. Zet de taken in de backlog.
4. Begin met het genereren van de `models.py` en schrijf direct de bijbehorende pytest fixtures en tests.
