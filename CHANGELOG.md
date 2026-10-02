# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

## [0.11.3] - 2026-10-02

### Fixed

- **Discord Notifications**: Fixed an issue where Discord DM notifications for card assignments were failing silently (or causing serialization errors in Celery) because the lazy translation Promise objects were not cast to strings before dispatch.
- **Chore**: Updated `.gitignore` to exclude standard build, testing, and temporary cache directories.

## [0.11.2] - 2026-09-29

### Added

- **Ticket System**: Added the ability to designate specific Global Labels as 'Ticket Labels' via the frontend Kanban settings. Only these designated labels will be available for users to select when submitting a new ticket.

## [0.11.0] - 2026-09-29

### Added

- **Discord Integration**: Added auto-invite functionality. All Auth Users linked to a `KanbanTeam` will now be automatically added to the Discord thread when a ticket is created.

## [0.10.2] - 2026-09-29

### Fixed

- **Discord Integration**: Fixed a missing argument in the Celery payload for `aadiscordbot`'s `run_task_function` which caused the bot consumer to crash silently.

## [0.10.1] - 2026-09-29

### Fixed

- **Discord Integration**: Fixed an issue where the Celery worker would silently fail to queue the Discord thread creation if the default Celery queue was used instead of the `aadiscordbot` queue.
- **Discord Integration**: Fixed an issue where thread creation would silently fail if the Discord channel was not cached by the bot by adding an API fetch fallback.
- **Ticket Submission**: Fixed a bug where a new ticket card could be placed in the wrong column due to a case-sensitive search for the default "Backlog" column name.

## [0.10.0] - 2026-09-29

### Added

- **Multilingual Support**: The project is now fully translatable. Added comprehensive Dutch (NL) and English (EN) language files for both frontend templates and backend logic.
- **Translation Infrastructure**: Integrated Django's `gettext` for extracting, compiling, and loading locale files.

### Changed

- **Settings UI**: Re-organized settings page into semantic tabs for better overview (Groups, Teams, Labels).
- **Settings Layout**: Fixed CSS styling for tab headers to prevent spacing issues.
- **Empty States**: Fixed UI layout issues on the Teams and Labels pages when no items are defined.

## [0.9.0] - 2026-09-29

### Added

- **Per-Board Ticket Configuration**: Moved the "Ticket Board" configuration from a global setting to a per-board setting. Boards can now be individually marked as ticket boards.
- **Per-Board Discord Channels**: Moved the "Discord Ticket Channel ID" from global settings to the individual boards. Tickets created for different teams/boards can now trigger threads in their own designated Discord channels.
- **Team-based Ticket Routing**: The ticket submission form now automatically routes new tickets to the correct board based on the selected target team. The board selection dropdown was removed for simplicity.

### Changed

- **UI Improvements**: Added a "Ticket Board" badge on the main boards overview to easily identify ticket boards.
- **Settings UI**: Split the Settings page into organized tabs (Groups, Teams, Labels) for better overview and management.
- **Summary View**: Fixed the summary view to properly display columns and cards from all boards instead of just the first one.
- **Clean up**: Removed unused global Discord ID settings and fixed UI issues with tab layouts.
- **Styling**: Fixed the editability of the card title label for better contrast and visibility in dark themes. Added cache busting to the CSS file to ensure styling updates propagate.

## [0.8.2] - 2026-09-28

### Fixed

- **Git Tracking**: Removed accidentally committed `.tmp-env` directory from git tracking and added it to `.gitignore`.

## [0.8.1] - 2026-09-28

### Fixed

- **CI/CD Pipeline**: Resolved pre-commit hook failures across multiple tools (Pylint, Flake8, ESLint, Stylelint, Isort/Black conflicts) to ensure GitHub Actions succeed.
- **Pylint Issues**: Fixed missing `HttpResponse` return statements in HTMX views (`edit_kanban_group`, `edit_kanban_team`).

## [0.8.0] - 2026-09-28

### Added

- **Discord Ticket System Integration**: Implemented member ticket submission UI with team assignments. Built a Discord integration to spawn ticket threads and sync messages. Added Discord Context Menu to upload standard messages as ticket comments.
- **Kanban Teams**: Added `KanbanTeam` model to decouple card assignments from view/write restrictions, and integrated team management into the frontend settings.
- **Auth Group Integration**: You can now assign Django Auth Groups directly to Kanban Groups via the Kanban Settings UI. This makes it easier to authorize larger groups of members at once instead of assigning them individually.

## [0.7.3] - 2026-09-26

### Added

- **API Services**: Added `aa_kanban.services` module providing a Python API (`create_kanban_board`, `create_kanban_card`, `move_kanban_card`) for safe interaction from external plugins (like aa-industry) ensuring business logic and webhooks are executed properly.

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
