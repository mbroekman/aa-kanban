# AA Kanban

Alliance Auth plugin for native Kanban boards.

## Features

- **Native Kanban boards** with an intuitive drag-and-drop interface and default columns (Backlog, To Do, In Progress, Review/Testing, Done).
- **Summary View** displaying all accessible boards across standardized status columns.
- **Global Labels & Card Colors**: Flexibly categorize cards using global labels and individual background colors, with automatic text-contrast adjustment.
- **Member Ticket System**: Allows regular members to submit tickets (cards) directly to a designated ticket board. The target ticket board can be easily configured via the frontend Kanban Settings page.
- **Permission management**: Manage read-only and write groups globally and per board directly from the frontend UI.
- **Discord Webhooks**: Receive global notifications when new boards are created, or board-specific notifications when cards are moved or new tickets are submitted.
- **Direct Messages (DMs)**: Discord DM notifications are sent directly to users when they are assigned to or removed from cards (requires the `aadiscordbot` app).

## Installation

```bash
pip install aa-kanban
```

Add the app to your `local.py`:

```python
INSTALLED_APPS += [
    "aa_kanban",
]
```

Run the database migrations:

```bash
python manage.py migrate
```

Gather static files:

```bash
python manage.py collectstatic
```

Restart your supervisor services to load the new code (e.g., gunicorn and celery).

## Discord Webhooks Configuration

To receive updates in your Discord channels, you can configure webhooks in the Django Admin panel:

1. **Global Board Creation Webhook**:
   - Go to **Admin** > **Kanban Settings** > **Global Kanban Settings**.
   - Fill in the **Board creation webhook** field with your Discord Webhook URL. You will receive a message whenever a new board is created.
2. **Board-Specific Card Movement Webhooks**:
   - Go to **Admin** > **Boards** and edit a specific board.
   - Fill in the **Discord webhook cards** field. Any card movements between lists on this board will be posted to this webhook.

## Settings

You can customize the application by adding the following settings to your `local.py`:

```python
# Change the name of the app in the Alliance Auth sidebar menu (default: "Kanban")
AA_KANBAN_APP_NAME = "Ticket System" 
```
