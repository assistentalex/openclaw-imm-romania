# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-03-30

### Added
- Initial release
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

## [Unreleased]

### Planned
- Contacts module
- Distribution lists management
- Room booking
- Delegate access support