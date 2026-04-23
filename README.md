<div align="center">

# NexLink — Exchange & Nextcloud Connector

**Email, files, tasks, and document workflows for teams**

**Built for [Firma de AI](https://firmade.ai), supported by [Firma de IT](https://firmade.it)**

[![Version](https://img.shields.io/badge/version-0.5.0-blue.svg)](https://github.com/asistent-alex/openclaw-nexlink)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-green.svg)](https://clawhub.ai)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![Firma de AI](https://img.shields.io/badge/built%20by-Firma%20de%20AI-6366f1.svg)](https://firmade.ai)
[![Firma de IT](https://img.shields.io/badge/supported%20by-Firma%20de%20IT-0ea5e9.svg)](https://firmade.it)

</div>

---

NexLink connects Microsoft Exchange and Nextcloud into one practical workflow layer — email, calendar, tasks, file management, and document understanding.

> Public positioning: **Firma de AI — Exchange & Nextcloud Assistant**  
> Internal skill / CLI name: **`nexlink`**

## What it does

This skill connects Exchange and Nextcloud into one practical workflow layer for:

- **Email** — read, send, draft, reply, forward, attachments
- **Calendar** — today, week, list, create, update, respond
- **Tasks** — list, create, complete, trash, delegate workflows
- **Analytics** — inbox stats, response time, top senders, heatmap, reports
- **Files** — list, search, upload, download, move, copy, info, sharing
- **Document understanding** — extract text, summarize, ask questions about one file
- **Workflow extraction** — extract actions from documents and create Exchange tasks

## Why this is useful

Use it when a team already works in **Microsoft Exchange** and **Nextcloud** and wants one assistant layer for:

- inbox and follow-up workflows
- meeting and task coordination
- file operations and sharing
- turning documents into action items

Built by [Firma de AI](https://firmade.ai), supported by [Firma de IT](https://firmade.it).

## Quick start

### Current CLI name

After installation, the command remains:

```bash
nexlink
```

### Typical first checks

```bash
nexlink mail connect
nexlink files list /
nexlink mail read --limit 5
nexlink cal today
nexlink tasks list
```

## Main capabilities

### Exchange — Email, Calendar, Tasks, Analytics

Full Exchange on-premises (2016/2019) workflows over EWS.

| What you can do | Command |
|---|---|
| Read email | `nexlink mail read` · `nexlink mail read --unread` · `nexlink mail get --id X` |
| Send email | `nexlink mail send --to x@y.com --subject "Hello" --body "..."` |
| Reply / forward | `nexlink mail reply --id EMAIL_ID --body "..."` · `nexlink mail forward --id EMAIL_ID --to other@example.com` |
| Download attachment | `nexlink mail download-attachment --id EMAIL_ID --name file.pdf` |
| Mark unread mail as read | `nexlink mail mark-all-read` |
| Today / week calendar | `nexlink cal today` · `nexlink cal week` |
| Create meeting | `nexlink cal create --subject "Meeting" --start "2026-04-20 14:00" --duration 60` |
| Create task | `nexlink tasks create --subject "Follow-up" --due "+7d" --priority high` |
| List delegated tasks | `nexlink tasks list --mailbox coleg@firma.ro` |
| Complete / trash task | `nexlink tasks complete --id TASK_ID` · `nexlink tasks trash --id TASK_ID` |
| Inbox analytics | `nexlink analytics stats --days 30` |

> Delegate workflows are supported where Exchange permissions allow them.

### Nextcloud — Files, Sharing, Document Understanding

Nextcloud workflows over WebDAV and OCS APIs.

| What you can do | Command |
|---|---|
| List files | `nexlink files list /Documents/` |
| Search files | `nexlink files search contract /Clients/` |
| Upload / download | `nexlink files upload /local/report.pdf /Documents/` · `nexlink files download /Documents/report.pdf /tmp/` |
| Create / move / copy | `nexlink files mkdir /Documents/New` · `nexlink files move /old /new` · `nexlink files copy /src /dst` |
| File info | `nexlink files info /Documents/report.pdf` |
| Shared items / public links | `nexlink files shared` · `nexlink files share-list` · `nexlink files share-create /Contracts/offer.pdf` |
| Extract text | `nexlink files extract-text /Clients/contract.docx` |
| Summarize a file | `nexlink files summarize /Clients/contract.docx` |
| Ask a file | `nexlink files ask-file /Clients/contract.docx "When is the renewal due?"` |
| Extract actions | `nexlink files extract-actions /Clients/contract.txt` |
| Create tasks from file | `nexlink files create-tasks-from-file /Clients/contract.txt --select 1,2 --execute` |

### Combined workflows

#### Send a Nextcloud file by email

```bash
nexlink files download /Documents/offer.pdf /tmp/
nexlink mail send --to "client@example.com" --subject "Offer" --body "Please see attached." --attach /tmp/offer.pdf
```

#### Save an email attachment into Nextcloud

```bash
nexlink mail download-attachment --id EMAIL_ID --name "contract.pdf" --output /tmp/
nexlink files upload /tmp/contract.pdf /Contracts/
```

#### Turn a document into follow-up tasks

```bash
nexlink files extract-actions /Clients/contract.txt
nexlink files create-tasks-from-file /Clients/contract.txt --select 1,2 --execute
```

## Configuration

### Exchange

```bash
export EXCHANGE_SERVER="https://mail.your-domain.com/EWS/Exchange.asmx"
export EXCHANGE_USERNAME="service-account"
export EXCHANGE_PASSWORD="your-password"
export EXCHANGE_EMAIL="service-account@your-domain.com"
export EXCHANGE_VERIFY_SSL="false"   # only for self-signed certificates
```

### Nextcloud

```bash
export NEXTCLOUD_URL="https://cloud.your-domain.com"
export NEXTCLOUD_USERNAME="your-username"
export NEXTCLOUD_APP_PASSWORD="your-app-password"
```

For full setup details, see [references/setup.md](references/setup.md).

## Installation options

### From Git

```bash
cd ~/.openclaw/skills/
git clone https://github.com/asistent-alex/openclaw-nexlink.git
cd openclaw-nexlink
pip3 install -r requirements.txt
```

### From ClawHub

Use the published listing/slug once the public package is live on ClawHub. The public title is intended to be:

**Firma de AI — Exchange & Nextcloud Assistant**

The CLI command remains:

```bash
nexlink
```

## Brand positioning

For public listings, release notes, and marketing copy, prefer:

- **Title:** Firma de AI — Exchange & Nextcloud Assistant
- **Subtitle:** Email, files, tasks, and document workflows for teams
- **Brand line:** Built by Firma de AI, supported by Firma de IT.
- **Links:** https://firmade.ai · https://firmade.it

## License

MIT — see [LICENSE](LICENSE).

This project follows the [Hardshell Coding Standards](https://github.com/asistent-alex/openclaw-hardshell).

---

<div align="center">

**Built by [Firma de AI](https://firmade.ai), supported by [Firma de IT](https://firmade.it)**  
*Exchange, Nextcloud, GitHub — one assistant.*

[Hardshell](https://github.com/asistent-alex/openclaw-hardshell) · [prompt-to-pr](https://github.com/asistent-alex/openclaw-prompt-to-pr) · [Report Bug](https://github.com/asistent-alex/openclaw-nexlink/issues) · [Request Feature](https://github.com/asistent-alex/openclaw-nexlink/issues)

</div>
