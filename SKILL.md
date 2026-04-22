---
name: imm-romania
version: 0.5.0
description: NexLink — Exchange & Nextcloud Connector. Built by Firma de AI and supported by Firma de IT. Integrates Exchange (email, calendar, tasks, analytics), Nextcloud (file management, sharing, text extraction, summarization, file Q&A, action extraction, task creation from files), and persistent memory via LCM plugin. Use when the user needs email operations, calendar management, task tracking, file operations, document summarization/Q&A, extracting actions from files, creating tasks from documents, email analytics, or combined workflows like "send report and archive copy", "create task from email", "schedule meeting with file attachment", "search conversation history", or "show email statistics".
validation: scripts/validate.sh
---

# NexLink — Exchange & Nextcloud Connector

**Built by [Firma de AI](https://firmade.ai), supported by [Firma de IT](https://firmade.it).**

This skill connects Exchange and Nextcloud into one practical workflow layer for:

- **Exchange**: email, calendar, tasks, analytics
- **Nextcloud**: file operations, sharing, document understanding, workflow extraction
- **Memory**: persistent context via LCM plugin

## Module Disponibile

| Modul | Descriere | Comandă |
|-------|-----------|---------|
| **Exchange** | Email, Calendar, Tasks, Analytics | `imm-romania <mail\|cal\|tasks\|analytics\|sync>` |
| **Nextcloud** | Fișiere, sharing, sumarizare, Q&A, extragere acțiuni | `imm-romania files <list\|search\|extract-text\|summarize\|ask-file\|extract-actions\|create-tasks-from-file\|...>` |
| **Memory** | Context persistent | Automat via LCM plugin |

## Ce rezolvă concret

Folosește skillul când vrei să lucrezi cu:

- emailuri, reply-uri, drafturi și atașamente în Exchange
- calendar, meeting-uri și follow-up tasks
- task-uri Exchange, inclusiv delegate access
- fișiere Nextcloud: listare, căutare, upload, download, mutare, sharing
- document understanding: extract-text, summarize, ask-file
- workflow extraction: extrage acțiuni din fișiere și creează task-uri Exchange
- context persistent între sesiuni prin LCM

## Utilizare Rapidă

### Email

```bash
# Conexiune
imm-romania mail connect

# Listează email-uri
imm-romania mail read --limit 10
imm-romania mail read --unread

# Trimite email
imm-romania mail send --to "client@example.com" --subject "Ofertă" --body "..."

# Răspunde
imm-romania mail reply --id EMAIL_ID --body "Răspuns"
```

### Calendar

```bash
# Evenimente
imm-romania cal today
imm-romania cal week
imm-romania cal list --days 7

# Creează eveniment
imm-romania cal create --subject "Meeting" --start "2024-01-15 14:00" --duration 60

# Cu invitați
imm-romania cal create --subject "Team Meeting" --start "2024-01-15 14:00" --to "user1@example.com,user2@example.com"
```

### Tasks

```bash
# Listează
imm-romania tasks list
imm-romania tasks list --overdue

# Creează
imm-romania tasks create --subject "Review proposal" --due "+7d" --priority high

# Completează
imm-romania tasks complete --id TASK_ID
```

### Analytics (Email Statistics)

```bash
# Statistici generale
imm-romania analytics stats --days 30

# Timp mediu de răspuns
imm-romania analytics response-time --days 7

# Top expeditori
imm-romania analytics top-senders --limit 20

# Activity heatmap
imm-romania analytics heatmap --days 30

# Statistici per folder
imm-romania analytics folders

# Raport complet
imm-romania analytics report --days 30
```

### Fișiere (Nextcloud)

```bash
# Listează și caută
imm-romania files list /Documents/
imm-romania files search contract /Clients/

# Upload / Download
imm-romania files upload /local/report.pdf /Documents/
imm-romania files download /Documents/report.pdf /local/

# Document understanding
imm-romania files extract-text /Clients/contract.docx
imm-romania files summarize /Clients/contract.docx
imm-romania files ask-file /Clients/contract.docx "When is the renewal due?"

# Workflow extraction
imm-romania files extract-actions /Clients/contract.txt
imm-romania files create-tasks-from-file /Clients/contract.txt
imm-romania files create-tasks-from-file /Clients/contract.txt --select 1,2 --execute
```

## Workflow-uri Combinate

### Email + Fișiere

Trimite email cu atașament din Nextcloud:

```bash
# Download din Nextcloud și trimite
imm-romania files download /Documents/offer.pdf /tmp/
imm-romania mail send --to "client@example.com" --subject "Ofertă" --body "..." --attach /tmp/offer.pdf
```

Salvează atașament din email în Nextcloud:

```bash
# Download atașament și upload în Nextcloud
imm-romania mail download-attachment --id EMAIL_ID --name "contract.pdf" --output /tmp/
imm-romania files upload /tmp/contract.pdf /Contracts/
```

### Calendar + Tasks

Creează task din meeting request:

```bash
# După meeting, creează task pentru follow-up
imm-romania tasks create --subject "Follow-up meeting X" --due "+3d"
```

### Memory (LCM Plugin)

Context persistent este gestionat automat de Lossless Context Management plugin.

Tool-uri disponibile (dacă plugin-ul e instalat):

- `lcm_grep` - Caută în istoricul conversațiilor
- `lcm_describe` - Detalii despre un summary
- `lcm_expand_query` - Expandare și răspuns la întrebări

Exemple:

- "Ce am discutat despre proiectul X?" → caută în istoric
- "Când am trimis ultimul email către Y?" → combină LCM cu Exchange

## Configurare Completă

Vezi [references/setup.md](references/setup.md) pentru configurare detaliată.

## Positioning public / branding

For public listings, documentation, and SEO copy, prefer this positioning:

- **Public title:** `Firma de AI — Exchange & Nextcloud Assistant`
- **Subtitle:** `Email, files, tasks, and document workflows for teams`
- **Brand line:** `Built by Firma de AI, supported by Firma de IT.`
- **Links:** `https://firmade.ai` și `https://firmade.it`

This keeps the internal skill name `imm-romania` while making the public positioning more accurate and searchable.

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

- Tasks sunt create în folderul Tasks al mailbox-ului implicit sau în mailbox-ul țintă când folosești delegate access
- Pentru task-uri collaborative, folosiți calendar events cu invitați
- Self-signed certificates necesită `verify_ssl: false`
- LCM plugin trebuie instalat separat: `openclaw plugins install @martian-engineering/lossless-claw`

## License

MIT License - see LICENSE file for details.
