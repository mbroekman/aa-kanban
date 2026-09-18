"""URL configuration for aa_kanban."""

from django.urls import path

from . import views, views_api

app_name = "aa_kanban"

urlpatterns = [
    # Board overview & detail
    path("", views.index, name="index"),
    path("board/<slug:board_slug>/", views.board_detail, name="board_detail"),
    # Board management (frontend)
    path("boards/create/", views.create_board, name="create_board"),
    path("boards/<slug:board_slug>/edit/", views.edit_board, name="edit_board"),
    path(
        "boards/<slug:board_slug>/delete/",
        views.delete_board,
        name="delete_board",
    ),
    # List (column) management via HTMX
    path(
        "boards/<slug:board_slug>/lists/create/",
        views_api.create_list,
        name="create_list",
    ),
    path(
        "lists/<int:list_id>/rename/",
        views_api.rename_list,
        name="rename_list",
    ),
    path(
        "lists/<int:list_id>/delete/",
        views_api.delete_list,
        name="delete_list",
    ),
    # Card management via HTMX
    path(
        "lists/<int:list_id>/cards/create/",
        views_api.create_card,
        name="create_card",
    ),
    # Existing card endpoints
    path("cards/<int:card_id>/move/", views_api.move_card, name="move_card"),
    path("cards/<int:card_id>/modal/", views_api.card_modal, name="card_modal"),
    path(
        "cards/<int:card_id>/comments/add/",
        views_api.add_comment,
        name="add_comment",
    ),
    path(
        "cards/<int:card_id>/assignees/toggle/",
        views_api.toggle_assignee,
        name="toggle_assignee",
    ),
    path(
        "cards/<int:card_id>/update/",
        views_api.update_card,
        name="update_card",
    ),
]

