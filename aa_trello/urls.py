"""URL configuration for aa_trello."""

from django.urls import path

from . import views

app_name = "aa_trello"

urlpatterns = [
    path("", views.index, name="index"),
]
