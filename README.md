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

NexLink connects Microsoft Exchange and Nextcloud into one practical workflow layer — email, calendar, tasks, file management, document understanding, and persistent context through OpenClaw.

> Public positioning: **Firma de AI — Exchange & Nextcloud Assistant**  
> Internal skill / CLI name: **`imm-romania`**

## What it does

This skill connects Exchange and Nextcloud into one practical workflow layer for:

- **Email** — read, send, draft, reply, forward, attachments
- **Calendar** — today, week, list, create, update, respond
- **Tasks** — list, create, complete, trash, delegate workflows
- **Analytics** — inbox stats, response time, top senders, heatmap, reports
- **Files** — list, search, upload, download, move, copy, info, sharing
- **Document understanding** — extract text, summarize, ask questions about one file
- **Workflow extraction** — extract actions from documents and create Exchange tasks
- **Persistent memory** — optional LCM integration for conversation continuity

## Why this is useful

Use it when a team already works in **Microsoft Exchange** and **Nextcloud** and wants one assistant layer for:

- inbox and follow-up workflows
- meeting and task coordination
- file operations and sharing
- turning documents into action items
- searching prior conversation context while working

Built by [Firma de AI](https://firmade.ai), supported by [Firma de IT](https://firmade.it).

## Quick start

### Current CLI name

After installation, the command remains:

```bash
imm-romania
```

### Typical first checks

```bash
imm-romania mail connect
imm-romania files list /
imm-romania mail read --limit 5
imm-romania cal today
imm-romania tasks list
```

## Main capabilities

### Exchange — Email, Calendar, Tasks, Analytics

Full Exchange on-premises (2016/2019) workflows over EWS.

| What you can do | Command |
|---|---|
| Read email | `imm-romania mail read` · `imm-romania mail read --unread` · `imm-romania mail get --id X` |
| Send email | `imm-romania mail send --to x@y.com --subject "Hello" --body "..."` |
| Reply / forward | `imm-romania mail reply --id EMAIL_ID --body "..."` · `imm-romania mail forward --id EMAIL_ID --to other@example.com` |
| Download attachment | `imm-romania mail download-attachment --id EMAIL_ID --name file.pdf` |
| Mark unread mail as read | `imm-romania mail mark-all-read` |
| Today / week calendar | `imm-romania cal today` · `imm-romania cal week` |
| Create meeting | `imm-romania cal create --subject "Meeting" --start "2026-04-20 14:00" --duration 60` |
| Create task | `imm-romania tasks create --subject "Follow-up" --due "+7d" --priority high` |
| List delegated tasks | `imm-romania tasks list --mailbox coleg@firma.ro` |
| Complete / trash task | `imm-romania tasks complete --id TASK_ID` · `imm-romania tasks trash --id TASK_ID` |
| Inbox analytics | `imm-romania analytics stats --days 30` |

> Delegate workflows are supported where Exchange permissions allow them.

### Nextcloud — Files, Sharing, Document Understanding

Nextcloud workflows over WebDAV and OCS APIs.

| What you can do | Command |
|---|---|
| List files | `imm-romania files list /Documents/` |
| Search files | `imm-romania files search contract /Clients/` |
| Upload / download | `imm-romania files upload /local/report.pdf /Documents/` · `imm-romania files download /Documents/report.pdf /tmp/` |
| Create / move / copy | `imm-romania files mkdir /Documents/New` · `imm-romania files move /old /new` · `imm-romania files copy /src /dst` |
| File info | `imm-romania files info /Documents/report.pdf` |
| Shared items / public links | `imm-romania files shared` · `imm-romania files share-list` · `imm-romania files share-create /Contracts/offer.pdf` |
| Extract text | `imm-romania files extract-text /Clients/contract.docx` |
| Summarize a file | `imm-romania files summarize /Clients/contract.docx` |
| Ask a file | `imm-romania files ask-file /Clients/contract.docx "When is the renewal due?"` |
| Extract actions | `imm-romania files extract-actions /Clients/contract.txt` |
| Create tasks from file | `imm-romania files create-tasks-from-file /Clients/contract.txt --select 1,2 --execute` |

### Combined workflows

#### Send a Nextcloud file by email

```bash
imm-romania files download /Documents/offer.pdf /tmp/
imm-romania mail send --to "client@example.com" --subject "Offer" --body "Please see attached." --attach /tmp/offer.pdf
```

#### Save an email attachment into Nextcloud

```bash
imm-romania mail download-attachment --id EMAIL_ID --name "contract.pdf" --output /tmp/
imm-romania files upload /tmp/contract.pdf /Contracts/
```

#### Turn a document into follow-up tasks

```bash
imm-romania files extract-actions /Clients/contract.txt
imm-romania files create-tasks-from-file /Clients/contract.txt --select 1,2 --execute
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

### Memory / LCM (optional)

Install the plugin separately if you want persistent conversation context:

```bash
openclaw plugins install @martian-engineering/lossless-claw
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
imm-romania
```

## Brand positioning

For public listings, release notes, and marketing copy, prefer:

- **Title:** Firma de AI — Exchange & Nextcloud Assistant
- **Subtitle:** Email, files, tasks, and document workflows for teams
- **Brand line:** Built by Firma de AI, supported by Firma de IT.
- **Links:** https://firmade.ai · https://firmade.it

## Roadmap

- [x] Exchange email workflows
- [x] Exchange calendar workflows
- [x] Exchange task workflows
- [x] Exchange analytics
- [x] Nextcloud file operations
- [x] Nextcloud document understanding
- [x] Document-to-task workflows
- [ ] Exchange contacts
- [ ] Email templates
- [ ] Calendar scheduling / find free slots
- [ ] Broader multilingual support

## License

MIT — see [LICENSE](LICENSE).

This project follows the [Hardshell Coding Standards](https://github.com/asistent-alex/openclaw-hardshell).

---

<div align="center">

**[Firma de AI](https://firmade.ai) · [Firma de IT](https://firmade.it) · Exchange + Nextcloud workflows with ☕**

[Hardshell](https://github.com/asistent-alex/openclaw-hardshell) · [prompt-to-pr](https://github.com/asistent-alex/openclaw-prompt-to-pr) · [Report Bug](https://github.com/asistent-alex/openclaw-nexlink/issues) · [Request Feature](https://github.com/asistent-alex/openclaw-nexlink/issues)

</div>
