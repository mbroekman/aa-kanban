"""Views for aa_trello."""

from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import render


@login_required
@permission_required("aa_trello.basic_access")
def index(request):
    """Render the main index page."""
    context = {
        "title": "AA Trello",
    }
    return render(request, "aa_trello/index.html", context)
