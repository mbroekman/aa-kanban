"""URL configuration for aa_kanban."""

from django.urls import path

from . import views, views_api, views_settings

app_name = "aa_kanban"

urlpatterns = [
    # Board overview & detail
    path("", views.index, name="index"),
    path("summary/", views.summary, name="summary"),
    path("tickets/create/", views.create_ticket, name="create_ticket"),
    path("tickets/success/", views.ticket_success, name="ticket_success"),
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
        "lists/<int:list_id>/edit/",
        views_api.edit_list,
        name="edit_list",
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
    path(
        "cards/<int:card_id>/color/",
        views_api.update_card_color,
        name="update_card_color",
    ),
    path(
        "cards/<int:card_id>/delete/",
        views_api.delete_card,
        name="delete_card",
    ),
    path(
        "cards/<int:card_id>/labels/toggle/",
        views_api.toggle_label,
        name="toggle_label",
    ),
    # Labels management (per board) via HTMX
    path(
        "boards/<slug:board_slug>/labels/modal/",
        views_api.board_labels_modal,
        name="board_labels_modal",
    ),
    path(
        "boards/<slug:board_slug>/labels/create/",
        views_api.create_label,
        name="create_label",
    ),
    path(
        "boards/<slug:board_slug>/labels/<int:label_id>/delete/",
        views_api.delete_label,
        name="delete_label",
    ),
    # Settings and Groups
    path("settings/", views_settings.kanban_settings, name="settings"),
    path("settings/groups/create/", views_settings.create_kanban_group, name="create_group"),
    path("settings/groups/<int:group_id>/edit/", views_settings.edit_kanban_group, name="edit_group"),
    path("settings/groups/<int:group_id>/delete/", views_settings.delete_kanban_group, name="delete_group"),
    path("settings/groups/<int:group_id>/users/", views_settings.group_users_modal, name="group_users_modal"),
    path("settings/groups/<int:group_id>/users/add/", views_settings.add_user_to_group, name="add_user_to_group"),
    path("settings/groups/<int:group_id>/users/<int:user_id>/remove/", views_settings.remove_user_from_group, name="remove_user_from_group"),
    path("settings/labels/create/", views_settings.create_settings_label, name="create_settings_label"),
    path("settings/labels/<int:label_id>/delete/", views_settings.delete_settings_label, name="delete_settings_label"),
    path("settings/global/update/", views_settings.update_global_settings, name="update_global_settings"),
]

