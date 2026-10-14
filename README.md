# AA Kanban

[![PyPI version](https://img.shields.io/pypi/v/aa-kanban)](https://pypi.org/project/aa-kanban/)
[![Python versions](https://img.shields.io/pypi/pyversions/aa-kanban)](https://pypi.org/project/aa-kanban/)
[![Tests](https://github.com/mbroekman/aa-kanban/actions/workflows/automated-checks.yml/badge.svg)](https://github.com/mbroekman/aa-kanban/actions/workflows/automated-checks.yml)

Alliance Auth plugin for native Kanban boards.

## Features

- **Native Kanban boards** with an intuitive drag-and-drop interface for cards and columns, complete with default columns (Backlog, To Do, In Progress, Review/Testing, Done). Columns can be rearranged dynamically via drag-and-drop, and newly created columns are immediately usable without a page refresh.
- **Summary View** displaying all accessible boards across standardized status columns.
- **Rich Card & Ticket Descriptions**: Markdown formatting with safe, sanitized rendering. Add images by pasting (`Ctrl+V`), dragging-and-dropping, or using the upload button, with a live `[Write]` / `[Preview]` toggle and a fullscreen lightbox for viewing.
- **Global Labels & Card Colors**: Flexibly categorize cards using global labels and individual background colors, with automatic text-contrast adjustment.
- **Member Ticket System**: Allows regular members to submit tickets (cards). Tickets are automatically routed to the correct board based on the selected target team. Boards can be individually designated as ticket boards. When a Discord ticket thread is created, members of the assigned team are automatically invited to the thread.
- **Permission management**: Manage read-only and write groups globally and per board directly from the frontend UI. Easily authorize large numbers of members by linking Django Auth Groups directly to Kanban groups. Board/settings management access can also be granted per Kanban Group (`can_manage_boards`) entirely from the frontend, without needing Django admin access.
- **Discord Integrations**: Receive notifications via Webhooks when boards are created or cards are moved. Ticket threads are automatically generated in configured channels, and Discord DM notifications are sent directly to users when they are assigned to cards (requires the `aadiscordbot` app).
- **Multilingual Support**: Fully supports English and Dutch language interfaces.

## Documentation

For a comprehensive guide covering all features, workflows, and frontend administration with screenshots, please see the [User & Administration Manual](docs/user_manual.md).

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
3. **Board-Specific Ticket Channel**:
   - Go to **Admin** > **Boards** and edit a specific board.
   - Fill in the **Discord Ticket Channel ID** field. New tickets submitted to this board will automatically create a thread in this channel. If the ticket is assigned to a `KanbanTeam`, all team members will be automatically invited to the thread.

## Settings

You can customize the application by adding the following settings to your `local.py`:

```python
# Change the name of the app in the Alliance Auth sidebar menu (default: "Kanban")
AA_KANBAN_APP_NAME = "Ticket System" 
```

## Periodic Tasks (Celery Beat)

To enable automatic hourly alerts for stale/inactive cards on boards that have `stale_card_alert_hours` configured, add the following task to your `local.py`:

```python
CELERYBEAT_SCHEDULE["aa_kanban_check_stale_cards"] = {
    "task": "aa_kanban.tasks.check_stale_cards",
    "schedule": crontab(minute="0", hour="*"),
}
```

To enable daily auto-archiving of cards that have sat in a board's last list past its configured `archive_after_days`, add:

```python
CELERYBEAT_SCHEDULE["aa_kanban_archive_done_cards"] = {
    "task": "aa_kanban.tasks.archive_done_cards",
    "schedule": crontab(minute="0", hour="3"),
}
```
