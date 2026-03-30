# IMM-Romania

**Email, Calendar și Tasks pentru Exchange on-premises**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Descriere

IMM-Romania este un skill OpenClaw care oferă acces complet la Microsoft Exchange Server on-premises (2016/2019) prin EWS (Exchange Web Services). Ideal pentru IMM-uri din România care folosesc Exchange on-premises.

### Funcționalități

- 📧 **Email** - citire, trimitere, răspunsuri, draft-uri, atașamente
- 📅 **Calendar** - evenimente, întâlniri, disponibilitate, invitații
- ✅ **Tasks** - creare, listare, actualizare, completare

## Instalare

```bash
# Clonează sau descarcă skill-ul în directorul skills
cd ~/.openclaw/skills/
git clone https://github.com/your-repo/imm-romania.git

# Sau copiază manual directorul imm-romania
```

## Cerințe

### Exchange Server
- Microsoft Exchange Server 2016 sau 2019 (on-premises)
- EWS (Exchange Web Services) activat
- Cont cu permisiuni de mailbox

### Python Dependencies
```bash
pip3 install exchangelib requests_ntlm
```

## Configurare

### Variabile de Environment

```bash
export EXCHANGE_SERVER="https://mail.example.com/EWS/Exchange.asmx"
export EXCHANGE_USERNAME="your-username"
export EXCHANGE_PASSWORD="your-password"
export EXCHANGE_EMAIL="your-email@example.com"

# Opțional (pentru self-signed certificates)
export EXCHANGE_VERIFY_SSL="false"
```

### Fișier de Configurare

Creează `config.yaml`:

```yaml
exchange:
  server: https://mail.example.com/EWS/Exchange.asmx
  username: ${EXCHANGE_USERNAME}
  password: ${EXCHANGE_PASSWORD}
  email: your-email@example.com
  verify_ssl: false
```

## Utilizare

### Email Operations

```bash
# Test conexiune
python3 scripts/cli.py mail connect

# Listează email-uri
python3 scripts/cli.py mail read --limit 10
python3 scripts/cli.py mail read --folder Inbox --unread
python3 scripts/cli.py mail read --from "sender@example.com" --subject "important"

# Trimite email
python3 scripts/cli.py mail send \
  --to "recipient@example.com" \
  --subject "Hello" \
  --body "This is a test message"

# Email cu HTML
python3 scripts/cli.py mail send \
  --to "recipient@example.com" \
  --subject "HTML Email" \
  --body "<h1>Hello</h1><p>This is <b>HTML</b> content.</p>" \
  --html

# Răspunde
python3 scripts/cli.py mail reply --id EMAIL_ID --body "Thank you!"

# Marchează citit
python3 scripts/cli.py mail mark --id EMAIL_ID --read
```

### Calendar Operations

```bash
# Evenimentele de azi
python3 scripts/cli.py calendar today

# Evenimente săptămâna aceasta
python3 scripts/cli.py calendar week

# Listează evenimente
python3 scripts/cli.py calendar list --days 7
python3 scripts/cli.py calendar list --start "2024-01-01" --end "2024-01-31"

# Creează eveniment
python3 scripts/cli.py calendar create \
  --subject "Team Meeting" \
  --start "2024-01-15 14:00" \
  --duration 60 \
  --location "Conference Room"

# Eveniment cu invitați
python3 scripts/cli.py calendar create \
  --subject "Client Call" \
  --start "2024-01-15 15:00" \
  --to "client@example.com,colleague@example.com" \
  --reminder 15

# Actualizează eveniment
python3 scripts/cli.py calendar update --id EVENT_ID --location "Room 201"

# Răspunde la meeting
python3 scripts/cli.py calendar respond --id EVENT_ID --response accept --body "I'll be there"

# Șterge eveniment
python3 scripts/cli.py calendar delete --id EVENT_ID
```

### Tasks Operations

```bash
# Listează task-uri
python3 scripts/cli.py tasks list
python3 scripts/cli.py tasks list --all
python3 scripts/cli.py tasks list --status in_progress
python3 scripts/cli.py tasks list --overdue

# Creează task
python3 scripts/cli.py tasks create \
  --subject "Review proposal" \
  --body "Review and provide feedback" \
  --due "+7d" \
  --priority high

# Actualizează task
python3 scripts/cli.py tasks update --id TASK_ID --status in_progress

# Marchează complet
python3 scripts/cli.py tasks complete --id TASK_ID

# Șterge task
python3 scripts/cli.py tasks delete --id TASK_ID --hard
```

## Structură

```
imm-romania/
├── SKILL.md          # Documentație OpenClaw
├── README.md         # Acest fișier
├── LICENSE           # MIT License
├── config.template.yaml
├── .env.template
├── .gitignore
└── scripts/
    ├── __init__.py
    ├── cli.py        # Entry point unificat
    ├── config.py     # Gestionare configurație
    ├── connection.py # Conexiune Exchange
    ├── utils.py      # Funcții utilitare
    ├── mail.py       # Operații email
    ├── cal.py        # Operații calendar
    └── tasks.py      # Operații tasks
```

## Troubleshooting

### Eroare de conexiune

```
{"ok": false, "error": "Connection refused"}
```
- Verifică URL-ul serverului Exchange
- Verifică că EWS este activat
- Verifică credențialele

### SSL Certificate Error

```
{"ok": false, "error": "SSL certificate verify failed"}
```
- Setează `EXCHANGE_VERIFY_SSL=false` sau `verify_ssl: false` în config

### Autentificare eșuată

```
{"ok": false, "error": "Authentication failed"}
```
- Verifică username și password
- Verifică că utilizatorul are permisiuni de mailbox

## Limitări

- Task-urile sunt create în folderul Tasks al contului configurat
- Nu suportă delegarea task-urilor către alți utilizatori
- Pentru Exchange Online (Office 365), configurarea poate diferi

## Contribuții

Contribuțiile sunt binevenite! Te rog să:

1. Faci fork la repository
2. Creezi un branch pentru feature (`git checkout -b feature/amazing-feature`)
3. Comiți schimbările (`git commit -m 'Add amazing feature'`)
4. Faci push la branch (`git push origin feature/amazing-feature`)
5. Deschizi un Pull Request

## Licență

Acest proiect este licențiat sub MIT License - vezi fișierul [LICENSE](LICENSE) pentru detalii.

## Autori

- Dezvoltat pentru comunitatea OpenClaw
- Publicat pe ClawHub

## Suport

Pentru probleme și întrebări:
- Deschide un issue pe GitHub
- Discuții pe Discord: [OpenClaw Community](https://discord.com/invite/clawd)