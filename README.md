# AA Kanban

Alliance Auth plugin for native Kanban boards.

## Installation

```bash
pip install aa-kanban
```

Add to `local.py`:

```python
INSTALLED_APPS += [
    "aa_kanban",
]
```

Run migrations:

```bash
python manage.py migrate
```
