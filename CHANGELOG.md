# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.7.2] - 2026-09-26

### Changed
- **Dynamic Titles**: Updated frontend templates (Dashboard, Board Detail, Summary, Settings) to dynamically use the `AA_KANBAN_APP_NAME` setting for page titles and headers instead of hardcoded 'Kanban' text, ensuring UI consistency with the sidebar menu.

## [0.7.1] - 2026-09-26

### Fixed
- **Card Creation UI**: Fixed an issue where creating a new card would append plain text instead of rendering the full card element due to conflicting HTMX directives.

## [0.7.0] - 2026-09-25

### Added
- **Card Background Colors**: Added the ability to assign a background color to individual Kanban cards directly from the card details modal, featuring automatic text contrast switching.
- **Card Deletion**: Implemented the ability to delete cards from the board with proper confirmation dialogues and live UI updates.
- **Default Columns**: Newly created boards now come with 5 default columns (Backlog, To Do, In Progress, Review/Testing, Done).
- **Summary View**: A new overview page showing all boards with cards grouped by the default columns.
- **Summary Column Mapping**: The Summary View now intelligently maps custom column names to the 5 default categories using keyword detection.
- **Summary Mode UI**: Cards displayed in the Summary View are now streamlined (hiding descriptions, labels, and due dates) for a cleaner overview.
- **Global Labels**: Labels are now shared globally across all boards instead of being restricted per board.
- **Ticket System**: Added a member-facing ticket submission form. Tickets are created as cards on a configured ticket board (set in Kanban Settings) and trigger Discord notifications.
- **Settings UI**: Added a frontend interface to the Kanban Settings page to select and manage the global Ticket Board.

### Fixed
- **HTMX Card UI Updates**: Fixed an issue where updating card properties (labels, assignees, colors) would incorrectly append a duplicate card to the end of the column instead of updating it in-place.
- **WIP Limit UI Refreshes**: Fixed a JavaScript bug where updating the Work-In-Progress (WIP) limit of a column would cause the limit indicator to disappear until the page was refreshed.
- **Dark Mode Compatibility**: Fixed an issue where Kanban columns appeared blindingly white in dark Bootswatch themes. Implemented a smart, theme-agnostic overlay system that naturally lightens the base theme colors for columns and cards.

## [0.6.2] - 2026-09-22

### Added
- Implemented native-looking custom Bootstrap confirmation modals for all destructive actions via HTMX (`htmx:confirm`).
- Added description tooltips to column names and card titles for better UX.

## [0.6.1] - 2026-09-22

### Fixed
- Included missing database migrations in the build to prevent `OperationalError` when accessing lists.
- Fixed an issue where removing users or groups using HTMX failed with a 403 Forbidden error due to missing CSRF tokens on buttons outside of forms.

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
