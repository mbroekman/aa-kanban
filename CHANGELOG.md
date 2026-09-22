# Changelog

All notable changes to this project will be documented in this file.

## [0.6.0] - 2026-09-22

### Added
- **List Limits & Descriptions**: Added support for configuring Work-In-Progress (WIP) limits and descriptions for Kanban lists.
- **Dynamic Group Member Listing**: The list of members for Kanban groups now updates dynamically in the background when closing the user management modal.

### Changed
- Improved target list validation when moving cards to enforce WIP limits.
- Refactored list edit and group user endpoints to use HTMX `hx-swap-oob` for seamless UI updates.

## [0.5.0] - 2026-09-21

### Added
- **Discord notifications for card assignments**: Users now receive Discord Direct Messages (DMs) when they are assigned to or removed from a Kanban card (requires `aadiscordbot`).
- **Discord webhooks**: Added support for global board creation webhooks and board-specific card movement webhooks via the admin panel.
- **Labels**: Added a label management UI to categorize cards with customizable colors.
- **Groups**: Improved frontend settings for group management.
- Initial native Kanban boards with an intuitive drag-and-drop interface.
