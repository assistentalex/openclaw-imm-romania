# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-03-30

### Added

- **Task Sync Module**: Bidirectional sync with Exchange server
  - `sync sync` - Synchronize tasks with server
  - `sync status` - Show sync statistics
  - `sync reminders` - Email reminders for overdue/upcoming tasks
  - `sync link-calendar` - Create calendar event from task
- **Hardshell Coding Standards**: Applied to all Exchange modules
  - Black formatting (PEP 8)
  - Ruff linting (fixed unused imports)
  - Comprehensive test suite (24 tests passing)
- **Module Organization**: Clean separation of concerns
  - `modules/exchange/` - Email, Calendar, Tasks, Sync
  - `modules/nextcloud/` - File management
  - `scripts/imm-romania.py` - Unified CLI entry point
- **Documentation**: Setup guide, skill docs, coding standards

### Fixed

- Test imports for module paths
- CLI execution path in tests
- Duplicate function definitions removed

## [0.1.0] - 2026-03-30

### Added - Initial Release

- Email operations: connect, read, get, send, draft, reply, forward, mark, attachments
- Calendar operations: connect, list, today, week, get, create, update, delete, respond, availability
- Tasks operations: connect, list, get, create, update, complete, delete
- Unified CLI with `imm-romania mail|calendar|tasks` commands
- Configuration via environment variables or config file
- Self-signed certificate support via `verify_ssl: false`
- MIT License
- GitHub issue templates and PR template

## [2.0.0-alpha] - 2026-03-30

### Added - Meta-Skill Architecture

**Breaking Change**: Restructured as meta-skill with modular architecture.

- **Modules**: Separated Exchange and Nextcloud into independent modules
- **Exchange Module**: Email, Calendar, Tasks operations (moved from root)
- **Nextcloud Module**: File management via WebDAV (new)
- **Memory Integration**: Documentation for LCM plugin integration
- **Unified CLI**: New orchestrator `imm-romania.py` for all modules

### Added - Exchange Module

- All previous email, calendar, and tasks functionality
- Task sync with Exchange server
- Email reminders for overdue/upcoming tasks
- Calendar event creation from tasks
- Logging system with JSON and colored output
- Complete test suite (9 tests passing)

### Added - Nextcloud Module

- File operations: upload, download, list, delete, move, copy
- Directory creation and management
- Automatic user ID resolution for WebDAV paths
- Error handling with specific exit codes

### Added - Memory (LCM Plugin)

- Documentation for Lossless Context Management plugin
- Instructions for persistent conversation history
- Tool descriptions: `lcm_grep`, `lcm_describe`, `lcm_expand_query`

### Added - Workflow Integrations

- Email + Files: Send attachments from Nextcloud
- Email + Files: Save attachments to Nextcloud
- Calendar + Tasks: Create calendar events from tasks
- Memory + All: Context-aware operations

### Changed - Architecture

- **Before**: Single skill with Exchange only
- **After**: Meta-skill orchestrating multiple modules
  - `modules/exchange/` - Email, Calendar, Tasks
  - `modules/nextcloud/` - File management
  - `references/setup.md` - Complete setup guide
  - `assets/config.template.yaml` - Configuration template

### Changed - Documentation

- New SKILL.md as meta-skill documentation
- Per-module SKILL.md files
- Comprehensive setup guide in `references/setup.md`
- Updated README with module structure

### Migration Guide (1.x to 2.0)

If upgrading from 1.x:

1. Update imports:
   ```python
   # Before
   from scripts.mail import MailClient
   
   # After
   from modules.exchange.mail import MailClient
   ```

2. Update CLI commands:
   ```bash
   # Before
   python3 scripts/cli.py mail connect
   
   # After (still works, but new unified CLI available)
   python3 scripts/imm-romania.py mail connect
   # Or simply
   imm-romania mail connect
   ```

3. New environment variables for Nextcloud:
   ```bash
   export NEXTCLOUD_URL="https://cloud.example.com"
   export NEXTCLOUD_USERNAME="your-username"
   export NEXTCLOUD_APP_PASSWORD="your-app-password"
   ```

---

## [1.0.0] - 2026-03-30

### Added

- Email operations: connect, read, get, send, draft, reply, forward, mark, attachments
- Calendar operations: connect, list, today, week, get, create, update, delete, respond, availability
- Tasks operations: connect, list, get, create, update, complete, delete
- Unified CLI with `imm-romania mail|calendar|tasks` commands
- Configuration via environment variables or config file
- Self-signed certificate support via `verify_ssl: false`
- MIT License
- GitHub issue templates and PR template

### Security

- Credentials only from environment variables (never hardcoded)
- SSL verification configurable for self-signed certificates

---

## [Unreleased]

### Planned

- Contacts module
- Distribution lists management
- Room booking
- Delegate access support
- Docker deployment
- ClawHub publication