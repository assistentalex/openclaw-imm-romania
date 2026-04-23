---
name: nexlink
version: 0.10.6
description: Nextcloud & Exchange connector for email, calendar, tasks, files, and document workflows.
metadata:
  openclaw:
    requires:
      bins:
        - python3
        - pip3
      env:
        - EXCHANGE_SERVER
        - EXCHANGE_USERNAME
        - EXCHANGE_PASSWORD
        - EXCHANGE_EMAIL
        - NEXTCLOUD_URL
        - NEXTCLOUD_USERNAME
        - NEXTCLOUD_APP_PASSWORD
    dependencies:
      - name: exchangelib
        type: pip
        version: ">=5.0.0"
      - name: requests_ntlm
        type: pip
        version: ">=1.1.0"
      - name: pdfplumber
        type: pip
        version: ">=0.10.0"
        optional: true
        description: "Document understanding features"
      - name: pytest
        type: pip
        version: ">=7.0.0"
        optional: true
        description: "Testing framework"
    primaryEnv: EXCHANGE_SERVER
    skillKey: "nexlink"
    emoji: "🔗"
    homepage: https://github.com/asistent-alex/openclaw-nexlink
    always: false
    author: Firma de AI
    links:
      homepage: https://firmade.ai
      repository: https://github.com/asistent-alex/openclaw-nexlink
---

# NexLink — Nextcloud & Exchange Connector

**Built by [Firma de AI](https://firmade.ai), supported by [Firma de IT](https://firmade.it).**

This skill connects Exchange and Nextcloud into one practical workflow layer for:

- **Exchange**: email, calendar, tasks, analytics
- **Nextcloud**: file operations, sharing, document understanding, workflow extraction

## Available Modules

| Module | Description | Command |
|--------|-------------|---------|
| **Exchange** | Email, Calendar, Tasks, Analytics | `nexlink <mail\|cal\|tasks\|analytics\|sync>` |
| **Nextcloud** | Files, sharing, summarization, Q&A, action extraction | `nexlink files <list\|search\|extract-text\|summarize\|ask-file\|extract-actions\|create-tasks-from-file\|...>` |

## What it solves

Use this skill when you want to work with:

- emails, replies, drafts and attachments in Exchange
- calendar, meetings and follow-up tasks
- Exchange tasks, including delegate access
- Nextcloud files: listing, search, upload, download, move, sharing
- document understanding: extract-text, summarize, ask-file
- workflow extraction: extract actions from files and create Exchange tasks

## Quick Start

### Email

```bash
# Connection
nexlink mail connect

# List emails
nexlink mail read --limit 10
nexlink mail read --unread

# Send email
nexlink mail send --to "client@example.com" --subject "Offer" --body "..."

# Reply
nexlink mail reply --id EMAIL_ID --body "Reply"
```

### Calendar

```bash
# Events
nexlink cal today
nexlink cal week
nexlink cal list --days 7

# Create event
nexlink cal create --subject "Meeting" --start "2024-01-15 14:00" --duration 60

# With attendees
nexlink cal create --subject "Team Meeting" --start "2024-01-15 14:00" --to "user1@example.com,user2@example.com"
```

### Tasks

```bash
# List
nexlink tasks list
nexlink tasks list --overdue

# Create
nexlink tasks create --subject "Review proposal" --due "+7d" --priority high

# Complete
nexlink tasks complete --id TASK_ID
```

### Analytics (Email Statistics)

```bash
# General statistics
nexlink analytics stats --days 30

# Average response time
nexlink analytics response-time --days 7

# Top senders
nexlink analytics top-senders --limit 20

# Activity heatmap
nexlink analytics heatmap --days 30

# Statistics per folder
nexlink analytics folders

# Full report
nexlink analytics report --days 30
```

### Files (Nextcloud)

```bash
# List and search
nexlink files list /Documents/
nexlink files search contract /Clients/

# Upload / Download
nexlink files upload /local/report.pdf /Documents/
nexlink files download /Documents/report.pdf /local/

# Document understanding
nexlink files extract-text /Clients/contract.docx
nexlink files summarize /Clients/contract.docx
nexlink files ask-file /Clients/contract.docx "When is the renewal due?"

# Workflow extraction
nexlink files extract-actions /Clients/contract.txt
nexlink files create-tasks-from-file /Clients/contract.txt
nexlink files create-tasks-from-file /Clients/contract.txt --select 1,2 --execute
```

## Combined Workflows

### Email + Files

Send email with attachment from Nextcloud:

```bash
# Download from Nextcloud and send
nexlink files download /Documents/offer.pdf /tmp/
nexlink mail send --to "client@example.com" --subject "Offer" --body "..." --attach /tmp/offer.pdf
```

Save attachment from email to Nextcloud:

```bash
# Download attachment and upload to Nextcloud
nexlink mail download-attachment --id EMAIL_ID --name "contract.pdf" --output /tmp/
nexlink files upload /tmp/contract.pdf /Contracts/
```

### Calendar + Tasks

Create task from meeting request:

```bash
# After meeting, create follow-up task
nexlink tasks create --subject "Follow-up meeting X" --due "+3d"
```

## Full Configuration

See [references/setup.md](references/setup.md) for detailed configuration.

## Positioning public / branding

For public listings, documentation, and SEO copy, prefer this positioning:

- **Public title:** `Firma de AI — Exchange & Nextcloud Assistant`
- **Subtitle:** `Email, files, tasks, and document workflows for teams`
- **Brand line:** `Built by Firma de AI, supported by Firma de IT.`
- **Links:** `https://firmade.ai` and `https://firmade.it`

This keeps the internal skill name `nexlink` while making the public positioning more accurate and searchable.

## Coding Standards

This project follows the [Hardshell Coding Standards](https://github.com/asistent-alex/openclaw-hardshell).

When writing or modifying Python code, see:
- **[Python Standards](https://github.com/asistent-alex/openclaw-hardshell/blob/main/references/languages/python.md)** - PEP 8, type hints, docstrings, security
- **[Testing Standards](https://github.com/asistent-alex/openclaw-hardshell/blob/main/references/testing.md)** - TDD, test pyramid, coverage
- **[Git Workflow](https://github.com/asistent-alex/openclaw-hardshell/blob/main/references/git-workflow.md)** - Conventional commits, PR process

Key rules:

- **PEP 8 formatting** - use `black` for formatting, `ruff` for linting
- **Type hints** - required for all function parameters and return types
- **Docstrings** - Google-style for all public functions and classes
- **Testing** - `pytest` with `pytest-cov` for coverage
- **Security** - never use `pickle` or `eval()` on untrusted input
- **Dependencies** - use `uv` or `poetry`, pin versions, audit with `pip-audit`

## Module Structure

```
modules/
├── exchange/           # Email, Calendar, Tasks (Exchange on-prem)
│   ├── SKILL.md       # Module documentation
│   ├── mail.py        # Email operations
│   ├── cal.py         # Calendar operations
│   ├── tasks.py       # Task operations
│   ├── sync.py        # Sync and reminders
│   └── ...
├── nextcloud/          # File management, doc understanding, workflow extraction
│   ├── SKILL.md       # Module documentation
│   └── nextcloud.py   # File operations and analysis
└── (future modules)
```

## Notes

- Tasks are created in the default mailbox's Tasks folder or in the target mailbox when using delegate access
- For collaborative tasks, use calendar events with attendees
- Self-signed certificates require `verify_ssl: false`

## License

MIT License - see LICENSE file for details.
