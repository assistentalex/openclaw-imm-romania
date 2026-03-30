# IMM-Romania

Email, Calendar și Tasks pentru Exchange on-premises. Ideal pentru IMM-uri din România.

## Descriere

Acest skill oferă acces complet la funcționalitățile Microsoft Exchange Server on-premises (2016/2019) prin EWS (Exchange Web Services):

- **Email:** citire, trimitere, răspunsuri, draft-uri, atașamente
- **Calendar:** evenimente, întâlniri, disponibilitate, invitații
- **Tasks:** creare, listare, actualizare, completare

## Cerințe

- Exchange Server 2016 sau 2019 (on-premises)
- EWS activat pe server
- Cont cu permisiuni de mailbox

## Configurare

Setează variabilele de environment:

```bash
export EXCHANGE_SERVER="https://mail.example.com/EWS/Exchange.asmx"
export EXCHANGE_USERNAME="your-username"
export EXCHANGE_PASSWORD="your-password"
export EXCHANGE_EMAIL="your-email@example.com"
```

Sau folosește un fișier de configurare `config.yaml`:

```yaml
exchange:
  server: https://mail.example.com/EWS/Exchange.asmx
  username: ${EXCHANGE_USERNAME}
  password: ${EXCHANGE_PASSWORD}
  email: your-email@example.com
  verify_ssl: false  # pentru self-signed certs
```

## Utilizare

### Email

```bash
# Test conexiune
imm-romania mail connect

# Listează email-uri
imm-romania mail read --limit 10
imm-romania mail read --folder Inbox --unread
imm-romania mail read --from "boss@company.com"

# Trimite email
imm-romania mail send --to "user@example.com" --subject "Hello" --body "Message"

# Răspunde
imm-romania mail reply --id EMAIL_ID --body "Reply text"

# Atașamente
imm-romania mail list-attachments --id EMAIL_ID
imm-romania mail download-attachment --id EMAIL_ID --name "file.pdf"
```

### Calendar

```bash
# Listează evenimente
imm-romania calendar list --days 7
imm-romania calendar today
imm-romania calendar week

# Creează eveniment
imm-romania calendar create --subject "Meeting" --start "2024-01-15 14:00" --duration 60

# Cu invitați
imm-romania calendar create --subject "Team Meeting" --start "2024-01-15 14:00" --to "user1@example.com,user2@example.com"

# Actualizează
imm-romania calendar update --id EVENT_ID --location "Room 101"

# Răspunde la meeting
imm-romania calendar respond --id EVENT_ID --response accept
```

### Tasks

```bash
# Listează task-uri
imm-romania tasks list
imm-romania tasks list --overdue
imm-romania tasks list --status in_progress

# Creează task
imm-romania tasks create --subject "Review proposal" --due "+7d" --priority high

# Actualizează
imm-romania tasks update --id TASK_ID --status in_progress

# Marchează complet
imm-romania tasks complete --id TASK_ID

# Șterge
imm-romania tasks delete --id TASK_ID
```

### Sincronizare Task-uri

```bash
# Sincronizează task-uri cu Exchange
imm-romania sync sync

# Vezi status sincronizare
imm-romania sync status

# Trimite reminder pentru task-uri overdue/upcoming
imm-romania sync reminders --hours 24

# Dry-run (arată ce s-ar trimite)
imm-romania sync reminders --hours 24 --dry-run

# Creează eveniment calendar din task
imm-romania sync link-calendar --id TASK_ID --time "14:00" --duration 60

# Cu invitație la sine
imm-romania sync link-calendar --id TASK_ID --time "14:00" --invite
```

#### Funcționalități Sync

| Comandă | Descriere |
|---------|-----------|
| `sync sync` | Sincronizează bidirecțional cu Exchange |
| `sync status` | Afișează statistici și status sincronizare |
| `sync reminders` | Trimite email cu task-uri overdue/upcoming |
| `sync link-calendar` | Creează eveniment calendar din task |

#### State Tracking

- Sincronizarea salvează state în `~/.openclaw/workspace/memory/task-sync-state.json`
- Tracking prin `changekey` pentru detectare modificări
- Istoric complet al task-urilor sincronizate

## Module

| Modul | Comandă | Descriere |
|-------|---------|-----------|
| Email | `mail` | Operații email complete |
| Calendar | `calendar` sau `cal` | Gestionare evenimente și întâlniri |
| Tasks | `tasks` | Gestionare sarcini |
| Sync | `sync` | Sincronizare task-uri și reminder-uri |

## Triggers

Acest skill se activează pentru:
- Citirea/trimiterea email-uri
- Gestionarea calendarului și întâlnirilor
- Crearea și gestionarea task-urilor
- Întrebări despre program, email-uri, sarcini

## Note

- Task-urile sunt create în folderul Tasks al contului configurat
- Pentru Exchange Online (Office 365), configurarea poate diferi
- Self-signed certificates necesită `verify_ssl: false`

## Licență

MIT License - vezi fișierul LICENSE pentru detalii.