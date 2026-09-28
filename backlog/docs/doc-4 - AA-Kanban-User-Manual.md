---
id: doc-4
title: AA Kanban User Manual
type: guide
created_date: '2026-09-28 06:34'
---

# AA Kanban User Manual

Welcome to **AA Kanban**, a native, fully integrated task and project management solution for Alliance Auth. This guide explains all functionalities, views, and settings available to users, moderators, and administrators.

## Table of Contents

1. [Overview](#1-overview)
1. [Boards & Lists](#2-boards--lists)
1. [Cards & Tasks](#3-cards--tasks)
1. [Ticket System (Member Submissions)](#4-ticket-system-member-submissions)
1. [Discord Integration](#5-discord-integration)
1. [Settings & Access Control](#6-settings--access-control)

______________________________________________________________________

## 1. Overview

AA Kanban is designed to keep your team organized using a visual "Kanban" approach. Tasks are represented by **Cards** which live inside **Lists** (columns). These lists are grouped into **Boards**.

- **Dashboard / Summary View**: See an overview of all your tasks across all boards you have access to.
- **Drag & Drop**: Effortlessly move tasks between columns as work progresses.
- **Real-time Access**: Integrated directly into Alliance Auth, using your existing permissions and authentication.

______________________________________________________________________

## 2. Boards & Lists

### Creating a Board

If you have the `manage_boards` permission, you can create a new board from the main Dashboard:

1. Click **Create Board**.
1. Provide a **Name** and **Description**.
1. Upon creation, standard columns are automatically generated: *Backlog*, *To Do*, *In Progress*, *Review/Testing*, and *Done*.

### Managing Lists (Columns)

Inside a board, you can organize your workflow by managing the lists:

- **Add List**: Click "Add List" on the far right of the board.
- **Edit List**: Click the three dots (`...`) next to a list title to rename it.
- **Move List**: Use the Left/Right arrows in the list menu to reorder columns.
- **Delete List**: Remove a list entirely (note: this deletes all cards within the list).

______________________________________________________________________

## 3. Cards & Tasks

Cards represent individual tasks, ideas, or tickets.

### Creating a Card

Click the **+ Add Card** button at the bottom of any list to quickly add a new task.

### Editing & Managing a Card

Clicking on any card opens the **Card Detail Modal**. Here you can manage:

- **Title & Description**: Describe the task. Supports markdown-like formatting.
- **Due Date**: Assign a deadline. A calendar icon will appear on the card.
- **Color**: Assign a background color to the card for visual distinction (e.g., Red for critical bugs).
- **Assignees**: Assign one or more Alliance Auth users to the task.
- **Labels**: Tag the card with specific labels (e.g., *Frontend*, *Urgent*).
- **Comments**: Discuss the task with your team. Comments are logged with a timestamp.
- **Assigned Team**: Route the card to a specific department or group (e.g., *IT Support*, *HR*).

### Moving Cards

Simply **drag and drop** a card from one list to another to update its status.

______________________________________________________________________

## 4. Ticket System (Member Submissions)

The Ticket System allows regular members (who don't necessarily have access to manage boards) to submit requests, reports, or tasks directly to the relevant teams.

### Submitting a Ticket

Users with the `create_ticket` permission will see a **Submit Ticket** menu item.

1. Fill out the **Title** and **Description**.
1. Select an **Assigned Team** if the request is for a specific department.
1. Add relevant **Labels**.
1. Submit. The ticket is automatically routed to the designated Ticket Board.

### Ticket Board Designation

Administrators can designate one or more boards as "Ticket Boards" from the **Settings** menu. All member-submitted tickets will appear in the first column (*Backlog*) of these designated boards.

______________________________________________________________________

## 5. Discord Integration

AA Kanban comes with deep Discord integration, utilizing `aadiscordbot`.

### Ticket Threads & Syncing

When a user submits a new Ticket, the system automatically creates a **Discord Thread** in your designated Ticket Channel.

- **Syncing**: The `KanbanTicketCog` monitors the thread. Any message sent in the Discord thread is automatically synced as a **Comment** on the Kanban Card in the web UI.
- **Uploading Messages**: Using Discord Context Menus (Right Click on a message -> Apps -> Upload to Ticket), you can directly push important Discord messages from other channels into an active Kanban ticket as a comment!

### DM Notifications

- Users receive a Direct Message (DM) from the Auth Bot when they are **Assigned to** or **Removed from** a card.

### Webhook Notifications

- **Global Notifications**: Sends a webhook message to a channel whenever a completely new Board is created.
- **Board Notifications**: Sends a webhook message when a card is moved across lists (e.g., moved to *Done*).

______________________________________________________________________

## 6. Settings & Access Control

The **Settings** menu (accessible to users with `manage_boards` permissions) allows comprehensive management of the application directly from the frontend.

### Ticket Teams

Teams are used to route tickets to specific departments.

- **Create Teams**: Define teams like *Recon*, *HR*, or *IT*.
- **Discord Role ID**: Link a team to a Discord Role. When a ticket is assigned to this team, the associated Discord Role is pinged in the Ticket Thread.
- **Manage Members**: Add individual Alliance Auth users to teams.

### Access Control (Kanban Groups)

Kanban Groups determine who can view and edit specific boards.

- **Create Kanban Groups**: Create groups like *Directors*, *Line Members*, etc.
- **Link Auth Groups**: Instead of adding users manually, you can link standard Alliance Auth Groups directly to a Kanban Group (e.g., link the *Member* Auth Group to the *Line Members* Kanban Group).
- **Board Permissions**: On the Board Edit page, assign which Kanban Groups have **View** (Read-Only) or **Write** access.

### Global Labels & Settings

- **Global Labels**: Create colored labels that can be used across all boards.
- **Ticket Boards**: Select which boards receive member-submitted tickets.
- **Ticket Channel ID**: Enter the Discord Channel ID where new Ticket Threads should be spawned.

*(Note: Technical configurations such as Webhook URLs are securely managed within the standard Django Admin panel under `Boards` and `Kanban Settings`.)*

______________________________________________________________________

*End of Manual*
