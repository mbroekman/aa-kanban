---
id: doc-3
title: Discord Ticket System Integration
type: specification
created_date: '2026-09-27 17:56'
---

# Discord Ticket System Integration

## 1. Huidige Situatie & Verzoek

Gebruikers kunnen momenteel tickets inschieten via de webinterface, waarna deze op het Kanban board verschijnen. De wens is om een diepere, moderne integratie met Discord te bouwen.

**Verzoek (vanuit de community/gebruiker):**

1. Tickets moeten toegewezen kunnen worden aan een specifiek **team** (bijv. IT, HR, Diplo).
1. Er moet een vast **Ticket Channel** in Discord komen waar tickets binnenkomen als **Threads**.
1. De Thread moet automatisch de reporter en het toegewezen team **pingen/uitnodigen**.
1. **Updates** (comments, statuswijzigingen) op de web-Kanban moeten in de Discord Thread verschijnen.
1. **Context Menu actie**: Een Discord bericht kunnen selecteren (right-click -> Apps) en deze als comment uploaden in het ticket.

______________________________________________________________________

## 2. Analyse & Haalbaarheid

Deze functionaliteit is uitstekend haalbaar met behulp van de bestaande integratie via de `aadiscordbot` app. Het tilt aa-kanban naar een professioneel niveau dat vergelijkbaar is met bekende Discord ticket-bots, met het voordeel dat de web-interface (het Kanban-board) de "single source of truth" blijft.

### 2.1 Assigned Team (Teams / Departments)

- **Datamodel:** Het `Card` model wordt uitgebreid met een `assigned_group` (ForeignKey naar `KanbanGroup` of een directe referentie). Omdat we in de vorige feature al `django.contrib.auth.models.Group` mapping hebben toegevoegd, kunnen we Auth Groups koppelen aan Kanban groepen.
- **UI:** In het 'Submit Ticket' formulier voor leden komt een keuzelijst "Selecteer een Team/Afdeling", zodat het ticket direct wordt doorgezet (en eventueel gefilterd) naar de juiste groep.

### 2.2 Discord Threads & Mentions

- **Bot Integratie (Celery Tasks):** Bij de aanmaak van een ticket roept Django via een Celery Task de Discord-bot aan. De bot maakt in een centraal kanaal een **Thread** aan genaamd: `Ticket #123: [Titel]`.
- **Mentions:** Omdat AllianceAuth Discord ID's koppelt, kan de bot direct de reporter `pingen`. Daarnaast pingt de bot de Discord Role die hoort bij de gekozen `assigned_group`. Dit betrekt direct de juiste personen.
- **Datamodel (Card):** Er wordt een nieuw veld `discord_thread_id = models.BigIntegerField(null=True, blank=True)` aan de kaart toegevoegd om de koppeling te bewaren.

### 2.3 Bi-directionele Sync (Web \<-> Discord)

- **Web naar Discord:** Django `post_save` signals luisteren naar nieuwe `Comment` objecten of wijzigingen in de kolom van een `Card`. Een Celery taak stuurt vervolgens een notificatie of het commentaar direct naar de Discord thread via het `discord_thread_id`.
- **Discord naar Web (Optioneel, maar sterk aanbevolen):** We schrijven een *Cog* voor `aadiscordbot` met een `on_message` listener. Zodra een gebruiker een bericht plaatst in een Discord-kanaal dat bekend staat als een ticket-thread (`discord_thread_id`), wordt dat bericht via een API-call of directe database-entry opgeslagen als `Comment` in de Django database. Hierdoor ontstaat naadloze 2-way communicatie.

### 2.4 Upload Message to Ticket (Discord Context Command)

- **Message Command:** Binnen `aadiscordbot` registreren we een Context Menu command (right-click bericht -> Apps -> "Add to Kanban Ticket").
- **Logica:**
  - *Binnen een Ticket Thread:* Als de command in een gelinkte thread wordt gestart, weet de bot precies om welke Card het gaat. Het bericht, inclusief afzender en eventuele attachments (links), wordt gekopieerd als nieuw Comment op het webbord.
  - *Buiten een Ticket Thread:* Als het erbuiten wordt gebruikt, kan de bot een Modal venster tonen met de vraag: "Aan welk Ticket ID moet dit toegevoegd worden?", waarna hij de toewijzing maakt.

______________________________________________________________________

## 3. Technisch Implementatieplan

**Fase 1: Datamodel & UI Updates**

- Breid `Card` uit met `assigned_group` (FK) en `discord_thread_id` (BigIntegerField).
- Pas het Ticket-indienformulier in de web-UI aan voor het selecteren van groepen.
- Pas de API en UI aan om dit te ondersteunen.

**Fase 2: Thread Creatie & Pings (Web -> Discord)**

- Gebruik of breid de bestaande Celery hooks uit met een `create_ticket_thread(card_id)` task via `aadiscordbot`.
- Zorg voor webhook integratie voor de creatie van Threads (hiervoor moet de bot de `Create Public Threads` permissie hebben).
- Stuur bij creatie een bericht dat de juiste Auth/Discord rollen en reporter user pingt.

**Fase 3: 2-way Sync**

- Implementeer Celery tasks getriggerd door Django Signals om nieuwe Comments naar de Discord thread te sturen.
- Bouw een `KanbanTicketCog` voor `aadiscordbot` die luistert naar berichten in gekoppelde threads en ze opslaat in Django.

**Fase 4: Discord Context Commands**

- Voeg in de `KanbanTicketCog` het Discord Message Context Command toe voor het "Uploaden" van individuele losse Discord berichten als comments op een ticket.

## 4. Conclusie

Het voorstel is een perfecte aanvulling voor een systeem als Alliance Auth en past goed binnen de bestaande ecosysteem-architectuur van aa-kanban en aadiscordbot. Door in fases te werken, kunnen we snel de belangrijkste functionaliteit (het maken van Threads en pingen van Teams) opleveren, en de interactieve onderdelen in de loop van de sprints verfijnen.
