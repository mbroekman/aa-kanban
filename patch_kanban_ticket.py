import re

# 1. Update views.py
with open("aa_kanban/views.py", "r") as f:
    views_content = f.read()

# Filter teams
views_content = views_content.replace(
    'teams = KanbanTeam.objects.all().order_by("name")',
    'teams = KanbanTeam.objects.filter(ticket_board__is_ticket_board=True).order_by("name")'
)

# Update context dictionary in error branches
def replace_error_context(match):
    error_msg = match.group(1)
    return f'''context = {{
                "boards": ticket_boards,
                "labels": labels,
                "teams": teams,
                "title": title,
                "description": description,
                "label_id": int(label_id) if label_id and label_id.isdigit() else None,
                "assigned_team_id": int(assigned_team_id) if assigned_team_id and assigned_team_id.isdigit() else None,
                "error": _({error_msg}),
            }}'''

views_content = re.sub(
    r'context = \{\s*"boards": ticket_boards,\s*"labels": labels,\s*"teams": teams,\s*"error": _\((.*?)\),\s*\}',
    replace_error_context,
    views_content,
    flags=re.DOTALL
)

with open("aa_kanban/views.py", "w") as f:
    f.write(views_content)

# 2. Update ticket_form.html
with open("aa_kanban/templates/aa_kanban/ticket_form.html", "r") as f:
    template = f.read()

template = template.replace(
    '<input type="text" class="form-control" id="title" name="title" required placeholder="{% trans \'Brief description of the issue...\' %}">',
    '<input type="text" class="form-control" id="title" name="title" required placeholder="{% trans \'Brief description of the issue...\' %}" value="{{ title|default:\"\" }}">'
)

template = template.replace(
    '<textarea class="form-control" id="description" name="description" rows="5"></textarea>',
    '<textarea class="form-control" id="description" name="description" rows="5">{{ description|default:"" }}</textarea>'
)

template = template.replace(
    '<option value="{{ label.id }}">{{ label.name }}</option>',
    '<option value="{{ label.id }}" {% if label_id == label.id %}selected{% endif %}>{{ label.name }}</option>'
)

template = template.replace(
    '<option value="{{ team.id }}">{{ team.name }}</option>',
    '<option value="{{ team.id }}" {% if assigned_team_id == team.id %}selected{% endif %}>{{ team.name }}</option>'
)

with open("aa_kanban/templates/aa_kanban/ticket_form.html", "w") as f:
    f.write(template)

print("Patch applied.")
