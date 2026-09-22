"""Smoke test to verify pytest and testauth environment."""

import pytest
from django.apps import apps


def test_aa_kanban_app_installed():
    """Verify that aa_kanban app is installed in Django."""
    assert apps.is_installed("aa_kanban")


@pytest.mark.django_db
def test_django_db_access():
    """Verify that django test database is functional."""
    from django.contrib.auth.models import User

    user = User.objects.create_user(username="testuser", email="test@example.com")
    assert user.username == "testuser"
    assert User.objects.filter(username="testuser").exists()
