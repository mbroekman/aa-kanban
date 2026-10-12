# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Fixed

- **Card Description Edit/Preview Buttons Nearly Invisible on Darkly Theme (TASK-87)**: The true root cause of reports that the description could not be edited and the Preview toggle had "disappeared": the dark-theme CSS override for `.btn-outline-secondary` targeted Bootstrap's native `[data-bs-theme="dark"]` attribute, but Alliance Auth's theme switcher sets `html[data-theme="darkly"]` instead, so the override never applied. The Edit/Preview/Attach Image buttons were present and functional all along, just rendered nearly invisible (dark-grey text and border on a dark-grey background) by Bootswatch Darkly's defaults. Fixed the selector to also match `html[data-theme="darkly"]`, restoring visible contrast across every `.btn-outline-secondary` button in the app (card/ticket description editors, group and team management, etc.).
- **Card Description Stale State After Save**: Also hardened the save flow so it no longer relies on client-side guesswork: after saving, the server now re-renders the entire description block (toggle buttons, rendered view, and edit form) as a single out-of-band swap, eliminating a related edge case where a stale "Add description" prompt could linger after a description was first saved.

## [0.13.0] - 2026-10-12

### Added

- **Frontend-Managed Board Management Permission (TASK-84)**: Added `can_manage_boards` flag to `KanbanGroup` (migration `0023_kanbangroup_can_manage_boards`), so officers can grant access to the Settings page and board create/edit/delete entirely from the frontend Settings UI (direct membership or via a linked Auth Group), without needing Django admin access to assign the native `aa_kanban.manage_boards` permission. The native permission still works as a backward-compatible fallback.
- **Image Support in Card Descriptions & Tickets (TASK-77)**:
  - Added backend endpoint `/kanban/api/upload-image/` with 5MB size limit, MIME type, and magic bytes validation (PNG, JPEG, GIF, WebP).
  - Added `KanbanAttachment` model and migration `0022_kanbanattachment` for tracking uploaded media securely in `MEDIA_ROOT`.
  - Added clipboard paste (`Ctrl+V`), drag-and-drop, and file upload picker button (`[Attach Image]`) to both the card description editor and ticket submission form.
  - Added safe Markdown rendering engine (`aa_kanban.markdown`) with BeautifulSoup XSS sanitization, responsive image styling, and Bootstrap 5 fullscreen lightbox zoom modal on image click.
  - Added `/kanban/api/preview-markdown/` endpoint and live `[Write]` / `[Preview]` tabs in the ticket submission form and card modal.

### Fixed

- **Card Modal Infinite Spinner on Click (TASK-83)**: Fixed card detail modal hanging with an infinite loading spinner when clicked. Migrated modal loading from conflicting click attributes on the SortableJS drag handle to native Bootstrap 5 `show.bs.modal` event handling with `htmx.ajax`, added clean loading spinner resets on show/hidden lifecycle, and ensured modal event handlers run for both read-only and write users.
- **Card & Ticket Description Input Field Contrast (TASK-82)**: Restored standard Bootstrap 5 `.form-control` appearance on card and ticket description textareas, ensuring high contrast, crisp borders, and distinct input background matching other form fields across all dark and light themes (e.g. Darkly).

## [0.12.1] - 2026-10-11

### Fixed

- **i18n / Stale Card Alerts**: Converted hardcoded Dutch strings in stale card alert notifications to standard English and added Dutch translations in `django.po` so alerts properly respect the configured site language (English by default, Dutch when configured).
- **Stale Card Alert Throttling & Repeat Interval**: Added `stale_card_repeat_hours` setting to `Board` (default 24h, 0 for one-time alert only) and `last_stale_alert_at` to `Card` to prevent hourly Discord alert spam for inactive cards.
- **CI / Test Coverage**: Handled missing `discord` module gracefully in `tasks.py` and mocked `discord` in thread auto-invite tests so tests run reliably in clean environments without `aadiscordbot`/`py-cord` preinstalled. Added `py-cord` to test dependencies.

## [0.12.0] - 2026-10-10

### Added

- **Stale Card Alerting**: Added board setting `stale_card_alert_hours` to configure inactivity alerts for cards (measured in hours).
- **Discord Notifications**: Added automated hourly notifications for stale cards dispatched to the board's Discord Bot Channel ID (via `aadiscordbot`) and/or Discord Webhook URL.
- **Finished Columns Exclusion**: Excludes cards placed in finished/completed columns ('Done', 'Afgerond', etc.) from stale card warnings.
- **Comment Activity Tracking**: Inactivity evaluation counts both card edits and comments placed on the card.
- **Periodic Celery Task**: Added `check_stale_cards` scheduled hourly in Celery Beat.
- **Discord Ticket Thread Activity Notifications**: Updates to ticket cards linked to a Discord thread (`discord_thread_id`) are now automatically posted directly into the thread:
  - Column/status movements (`move_card` and `services.move_kanban_card`).
  - Label additions and removals (`toggle_label`).
  - Team assignments, role mentions, and auto-inviting new team members to the thread (`update_card_team`).
- **Auth Groups for KanbanTeam & Thread Auto-Invite**: Teams (`KanbanTeam`) now support linking Django Auth Groups (`Group`) alongside individual members via frontend settings (`team_users_modal`). Auto-invite to Discord ticket threads (both on creation and team reassignment) automatically invites all members from both direct assignments and linked Auth Groups.
- **Team Settings Modal**: Converted `edit_team_modal.html` into a full Bootstrap 5 modal dialog with global `closeModal` event handling for seamless HTMX closes.
- **Agent Guidelines**: Aligned `AGENTS.md`, `CLAUDE.md`, `GEMINI.md` and `.cursorrules` with the central workspace standards.

### Fixed

- **CI & Pre-Commit**: Resolved Flake8 E203 whitespace error in Discord message chunking, added E203 to Flake8 extend-ignore, and formatted markdown files with mdformat.
- **CI & Pre-Commit**: Excluded `backlog/` from the mdformat hook, since backlog-md rewrites task files in its own format and repeatedly broke CI.

## [0.11.4] - 2026-10-02

### Fixed

- **Ticket Submission**: Fixed a bug where regular users would see an empty dialog when creating a ticket because they could inadvertently select a team without a ticket board. The dropdown now only shows valid teams.
- **Ticket Submission**: Improved the ticket form to preserve user inputs (title, description) when a validation error occurs.

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
