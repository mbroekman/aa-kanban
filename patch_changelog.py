with open("CHANGELOG.md", "r") as f:
    content = f.read()

new_version = """## [0.11.4] - 2026-10-02

### Fixed

- **Ticket Submission**: Fixed a bug where regular users would see an empty dialog when creating a ticket because they could inadvertently select a team without a ticket board. The dropdown now only shows valid teams.
- **Ticket Submission**: Improved the ticket form to preserve user inputs (title, description) when a validation error occurs.

"""

content = content.replace("## [0.11.3]", new_version + "## [0.11.3]")

with open("CHANGELOG.md", "w") as f:
    f.write(content)

with open("aa_kanban/__init__.py", "w") as f:
    f.write('__version__ = "0.11.4"\n')

print("Changelog and init updated.")
