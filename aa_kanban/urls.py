"""URL configuration for aa_kanban."""

from django.urls import path

from . import views, views_api, views_intake, views_settings, views_spa_api

app_name = "aa_kanban"

urlpatterns = [
    # Board overview & detail
    path("", views.index, name="index"),
    path("summary/", views.summary, name="summary"),
    path("search/", views.search, name="search"),
    path("members/", views.members_index, name="members_index"),
    path("boards/archived/", views.archived_boards, name="archived_boards"),
    path("tickets/create/", views.create_ticket, name="create_ticket"),
    path("tickets/success/", views.ticket_success, name="ticket_success"),
    path("board/<slug:board_slug>/", views.board_detail, name="board_detail"),
    path(
        "board/<slug:board_slug>/archived/",
        views.archived_cards,
        name="archived_cards",
    ),
    # Board management (frontend)
    path("boards/create/", views.create_board, name="create_board"),
    path("boards/<slug:board_slug>/edit/", views.edit_board, name="edit_board"),
    path(
        "boards/<slug:board_slug>/delete/",
        views.delete_board,
        name="delete_board",
    ),
    path(
        "boards/<slug:board_slug>/archive/",
        views.archive_board,
        name="archive_board",
    ),
    path(
        "boards/<slug:board_slug>/restore/",
        views.restore_board,
        name="restore_board",
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
    path(
        "lists/<int:list_id>/move/",
        views_api.move_list,
        name="move_list",
    ),
    # Card management via HTMX
    path(
        "lists/<int:list_id>/cards/create/",
        views_api.create_card,
        name="create_card",
    ),
    # Existing card endpoints
    path("cards/<int:card_id>/move/", views_api.move_card, name="move_card"),
    path(
        "cards/<int:card_id>/close-thread/",
        views_api.close_card_thread,
        name="close_card_thread",
    ),
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
        "cards/<int:card_id>/team/",
        views_api.update_card_team,
        name="update_card_team",
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
    # Image upload and Markdown preview
    path("api/upload-image/", views_api.upload_image, name="upload_image"),
    path(
        "api/preview-markdown/",
        views_api.preview_markdown,
        name="preview_markdown",
    ),
    # Settings and Groups
    path("settings/", views_settings.kanban_settings, name="settings"),
    path(
        "settings/groups/create/",
        views_settings.create_kanban_group,
        name="create_group",
    ),
    path(
        "settings/groups/<int:group_id>/edit/",
        views_settings.edit_kanban_group,
        name="edit_group",
    ),
    path(
        "settings/groups/<int:group_id>/delete/",
        views_settings.delete_kanban_group,
        name="delete_group",
    ),
    path(
        "settings/groups/<int:group_id>/users/",
        views_settings.group_users_modal,
        name="group_users_modal",
    ),
    path(
        "settings/groups/<int:group_id>/users/add/",
        views_settings.add_user_to_group,
        name="add_user_to_group",
    ),
    path(
        "settings/groups/<int:group_id>/users/<int:user_id>/remove/",
        views_settings.remove_user_from_group,
        name="remove_user_from_group",
    ),
    path(
        "settings/groups/<int:group_id>/authgroups/add/",
        views_settings.add_authgroup_to_group,
        name="add_authgroup_to_group",
    ),
    path(
        "settings/groups/<int:group_id>/authgroups/<int:authgroup_id>/remove/",
        views_settings.remove_authgroup_from_group,
        name="remove_authgroup_from_group",
    ),
    path(
        "settings/labels/create/",
        views_settings.create_settings_label,
        name="create_settings_label",
    ),
    path(
        "settings/labels/<int:label_id>/edit/",
        views_settings.edit_settings_label,
        name="edit_settings_label",
    ),
    path(
        "settings/labels/<int:label_id>/delete/",
        views_settings.delete_settings_label,
        name="delete_settings_label",
    ),
    path(
        "settings/global/update/",
        views_settings.update_global_settings,
        name="update_global_settings",
    ),
    path(
        "settings/teams/create/",
        views_settings.create_kanban_team,
        name="create_kanban_team",
    ),
    path(
        "settings/teams/<int:team_id>/edit/",
        views_settings.edit_kanban_team,
        name="edit_kanban_team",
    ),
    path(
        "settings/teams/<int:team_id>/delete/",
        views_settings.delete_kanban_team,
        name="delete_kanban_team",
    ),
    path(
        "settings/teams/<int:team_id>/users/",
        views_settings.team_users_modal,
        name="team_users_modal",
    ),
    path(
        "settings/teams/<int:team_id>/users/add/",
        views_settings.add_user_to_team,
        name="add_user_to_team",
    ),
    path(
        "settings/teams/<int:team_id>/users/<int:user_id>/remove/",
        views_settings.remove_user_from_team,
        name="remove_user_from_team",
    ),
    path(
        "settings/teams/<int:team_id>/authgroups/add/",
        views_settings.add_authgroup_to_team,
        name="add_authgroup_to_team",
    ),
    path(
        "settings/teams/<int:team_id>/authgroups/<int:authgroup_id>/remove/",
        views_settings.remove_authgroup_from_team,
        name="remove_authgroup_from_team",
    ),
    # Modern React + shadcn/ui SPA & JSON API
    path("spa/", views_spa_api.spa_app, name="spa_root"),
    path("spa/<path:subpath>", views_spa_api.spa_app, name="spa_subpath"),
    path("api/v1/boards/", views_spa_api.api_boards, name="spa_api_boards"),
    path(
        "api/v1/boards/create/",
        views_spa_api.api_create_board,
        name="spa_api_create_board",
    ),
    path(
        "api/v1/boards/archived/",
        views_spa_api.api_archived_boards,
        name="spa_api_archived_boards",
    ),
    path(
        "api/v1/boards/<slug:board_slug>/",
        views_spa_api.api_board_detail,
        name="spa_api_board_detail",
    ),
    path(
        "api/v1/boards/<slug:board_slug>/edit/",
        views_spa_api.api_edit_board,
        name="spa_api_edit_board",
    ),
    path(
        "api/v1/boards/<slug:board_slug>/archive/",
        views_spa_api.api_archive_board,
        name="spa_api_archive_board",
    ),
    path(
        "api/v1/boards/<slug:board_slug>/restore/",
        views_spa_api.api_restore_board,
        name="spa_api_restore_board",
    ),
    path(
        "api/v1/boards/<slug:board_slug>/delete/",
        views_spa_api.api_delete_board,
        name="spa_api_delete_board",
    ),
    path(
        "api/v1/boards/<slug:board_slug>/archived-cards/",
        views_spa_api.api_archived_cards,
        name="spa_api_archived_cards",
    ),
    path(
        "api/v1/boards/<slug:board_slug>/lists/create/",
        views_spa_api.api_create_list,
        name="spa_api_create_list",
    ),
    path(
        "api/v1/lists/<int:list_id>/edit/",
        views_spa_api.api_edit_list,
        name="spa_api_edit_list",
    ),
    path(
        "api/v1/lists/<int:list_id>/delete/",
        views_spa_api.api_delete_list,
        name="spa_api_delete_list",
    ),
    path(
        "api/v1/lists/<int:list_id>/cards/create/",
        views_spa_api.api_create_card,
        name="spa_api_create_card",
    ),
    path(
        "api/v1/cards/<int:card_id>/",
        views_spa_api.api_card_detail,
        name="spa_api_card_detail",
    ),
    path(
        "api/v1/cards/<int:card_id>/update/",
        views_spa_api.api_update_card,
        name="spa_api_update_card",
    ),
    path(
        "api/v1/cards/<int:card_id>/move/",
        views_spa_api.api_move_card,
        name="spa_api_move_card",
    ),
    path(
        "api/v1/cards/<int:card_id>/restore/",
        views_spa_api.api_restore_card,
        name="spa_api_restore_card",
    ),
    path(
        "api/v1/cards/<int:card_id>/delete/",
        views_spa_api.api_delete_card,
        name="spa_api_delete_card",
    ),
    path(
        "api/v1/cards/<int:card_id>/comments/add/",
        views_spa_api.api_add_comment,
        name="spa_api_add_comment",
    ),
    path("api/v1/search/", views_spa_api.api_search, name="spa_api_search"),
    path("api/v1/summary/", views_spa_api.api_summary, name="spa_api_summary"),
    path(
        "api/v1/tickets/options/",
        views_spa_api.api_ticket_options,
        name="spa_api_ticket_options",
    ),
    path(
        "api/v1/tickets/create/",
        views_spa_api.api_create_ticket,
        name="spa_api_create_ticket",
    ),
    path("api/v1/settings/", views_spa_api.api_settings, name="spa_api_settings"),
    path(
        "api/v1/settings/global/update/",
        views_spa_api.api_update_global_settings,
        name="spa_api_update_global_settings",
    ),
    path(
        "api/v1/settings/groups/save/",
        views_spa_api.api_save_group,
        name="spa_api_save_group",
    ),
    path(
        "api/v1/settings/groups/<int:group_id>/delete/",
        views_spa_api.api_delete_group,
        name="spa_api_delete_group",
    ),
    path(
        "api/v1/settings/teams/save/",
        views_spa_api.api_save_team,
        name="spa_api_save_team",
    ),
    path(
        "api/v1/settings/teams/<int:team_id>/delete/",
        views_spa_api.api_delete_team,
        name="spa_api_delete_team",
    ),
    path(
        "api/v1/settings/labels/save/",
        views_spa_api.api_save_label,
        name="spa_api_save_label",
    ),
    path(
        "api/v1/settings/labels/<int:label_id>/delete/",
        views_spa_api.api_delete_label,
        name="spa_api_delete_label",
    ),
    # Must stay LAST: Alliance Auth stops adding its login check to the patterns
    # after an excluded (public) view. Public because it uses an API key; needs
    # "aa_kanban" in APPS_WITH_PUBLIC_VIEWS.
    path(
        "api/intake/discord-thread/",
        views_intake.discord_thread_intake,
        name="intake_discord_thread",
    ),
]
