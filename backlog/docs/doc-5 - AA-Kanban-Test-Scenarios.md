---
id: doc-5
title: AA Kanban Test Scenarios
type: guide
created_date: '2026-09-28 11:26'
---

# AA Kanban Test Scenarios

This document contains comprehensive test scenarios to verify all functionality of the AA Kanban app, including its user interface, permission systems, and Discord integrations.

---

## 1. Core Kanban Functionality (UI & UX)

### 1.1 Boards
- [ ] **Create Board**: As a user with `manage_boards` permission, click "Create Board". Verify that a new board is created with default lists (Backlog, To Do, In Progress, Review/Testing, Done).
- [ ] **Edit Board**: Edit the board's name and description. Verify changes are reflected in the UI.
- [ ] **Delete Board**: Delete a board. Verify it disappears from the dashboard and database.

### 1.2 Lists (Columns)
- [ ] **Add List**: Create a new list on a board. Verify it appears on the far right.
- [ ] **Edit List**: Rename a list. Verify the name updates immediately via HTMX.
- [ ] **Move List**: Use the Left/Right arrows in the list menu. Verify the list changes order and the order persists after page reload.
- [ ] **Delete List**: Delete a list. Verify the list and all its cards are removed.

### 1.3 Cards (Tasks)
- [ ] **Create Card**: Add a new card to a list. Verify it appears at the bottom of the list.
- [ ] **Edit Card Details**: Open the card modal. Modify the Title, Description, and Due Date. Verify the changes are saved and reflected on the card in the list view.
- [ ] **Card Color**: Change the card's background color. Verify the color updates immediately and text contrast remains readable.
- [ ] **Card Movement**: Drag and drop a card to a different list. Verify its position is saved upon page reload.
- [ ] **Labels**: Add/Remove global labels to a card. Verify they appear on the card in the list view.
- [ ] **Comments**: Add a comment to the card. Verify it appears with the correct author and timestamp.
- [ ] **Delete Card**: Delete a card. Verify it is removed.

---

## 2. Settings & Access Control

### 2.1 Kanban Groups (Access Control)
- [ ] **Create Kanban Group**: In Settings, create a new Kanban Group (e.g., "QA Team").
- [ ] **Add/Remove Users**: Open the User Management modal for the group. Add a user, verify the member count increases. Remove the user, verify it decreases.
- [ ] **Link Auth Group**: In the same modal, link a Django Auth Group. Verify it is linked successfully.
- [ ] **Board Permissions (Enforcement)**: 
  - Edit a board and assign "QA Team" to **View Groups** (Read-Only).
  - Log in as a user inside "QA Team". Verify the user can see the board but *cannot* move cards, edit cards, or add lists.
  - Change "QA Team" to **Write Groups**. Verify the user can now move and edit cards.

### 2.2 Ticket Teams (Card Assignments)
- [ ] **Create Team**: In Settings, create a new Ticket Team (e.g., "IT Support").
- [ ] **Discord Role ID**: Edit the team and add a valid Discord Role ID.
- [ ] **Team Members**: Add users to the Team.
- [ ] **Assign Team to Card**: Open a card modal and assign it to "IT Support". Verify the Team badge appears on the card.
- [ ] **Assign User to Card**: Assign a specific user to a card. Verify their avatar/name appears on the card.

---

## 3. Ticket System (Member Submissions)

### 3.1 Submitting a Ticket
- [ ] **Ticket Form**: As a regular user with `create_ticket` permission (but NO `manage_boards` permission), click the "Submit Ticket" menu item.
- [ ] **Validation**: Submit an empty form. Verify form validation prevents submission.
- [ ] **Submission**: Fill out the Title, Description, assign a Team, and select a Label. Submit the ticket.
- [ ] **Routing**: Verify the user is redirected to the success page.
- [ ] **Board Arrival**: As a board admin, verify the ticket appears in the designated Ticket Board's first column (Backlog) with all selected attributes (Team, Labels).

---

## 4. Discord Integration

*Prerequisites: Celery must be running, Discord Bot must be active, and Webhooks/Channel IDs must be configured in Settings and Django Admin.*

### 4.1 Global Notifications
- [ ] **Board Creation Webhook**: Configure the Global Board Creation Webhook in Django Admin (`KanbanSetting`). Create a new board in the UI. Verify a Discord notification is sent announcing the new board.

### 4.2 Board Notifications
- [ ] **Card Movement Webhook**: Configure `discord_webhook_cards` on a specific board in Django Admin. Move a card from "To Do" to "Done". Verify a Discord notification is sent stating the card was moved.

### 4.3 Ticket Threads & Syncing
- [ ] **Thread Creation**: Configure `ticket_channel_id` in Settings. Have a user submit a new Ticket via the web UI. Verify a new Discord Thread is automatically created in the specified channel.
- [ ] **Role Pinging**: If the ticket was assigned to a Team with a `discord_role_id`, verify the Discord Thread mentions/pings that specific role.
- [ ] **Two-way Sync (Discord -> Web)**: Post a standard message in the newly created Discord Thread. Verify the message appears as a **Comment** on the corresponding Kanban Card in the web UI.

### 4.4 Upload to Ticket (Context Menu)
- [ ] **Upload Message**: In Discord, find any message in any channel. Right-click the message -> **Apps** -> **Upload to Ticket**.
- [ ] **Selection**: Follow the bot's prompt to select the target Kanban Card from the dropdown list.
- [ ] **Verification**: Verify the Discord message is successfully appended as a Comment on the selected Kanban Card in the web UI, preserving the original author and content.

### 4.5 Direct Message (DM) Notifications
- [ ] **Assign User**: Assign an Alliance Auth user to a card.
- [ ] **DM Receipt**: Verify the auth bot sends a Direct Message to the user's Discord account notifying them of the assignment.
- [ ] **Remove User**: Unassign the user from the card. Verify a DM is sent notifying them they were unassigned.

---
*End of Test Scenarios*

