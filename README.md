# AA Kanban

Alliance Auth plugin for native Kanban boards.

## Features

- **Native Kanban boards** with an intuitive drag-and-drop interface.
- **Permission management** per board (read-only and write groups).
- **Global Discord Webhooks** (Admin panel): Receive notifications when new boards are created.
- **Board-specific Discord Webhooks** (Admin panel): Receive notifications when cards are moved across lists on a specific board.
- **Direct Messages (DMs)**: Discord DM notifications are sent directly to users when they are assigned to or removed from cards (requires the `aadiscordbot` app to be installed and active).

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
