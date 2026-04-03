# IMM-Romania

**Asistent complet pentru IMM-uri din România - Email, Calendar, Tasks și Fișiere**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

## Descriere

IMM-Romania este un skill OpenClaw care integrează toate serviciile necesare pentru un IMM:

- 📧 **Exchange** - Email, Calendar, Tasks (on-premises 2016/2019)
- 📁 **Nextcloud** - Gestionare fișiere și colaborare
- 🧠 **Memory** - Context persistent prin LCM plugin

Ideal pentru întreprinderile mici și mijlocii din România care folosesc infrastructură on-premises.

## Module

| Modul | Serviciu | Descriere |
|-------|----------|-----------|
| **Exchange** | Email, Calendar, Tasks | Operații complete pentru Exchange on-premises |
| **Nextcloud** | Fișiere | Upload, download, organizare fișiere |
| **Memory** | Context | Istoric conversații persistente (LCM plugin) |

## Instalare

```bash
# Instalează în OpenClaw skills directory
cd ~/.openclaw/skills/
git clone https://github.com/assistentalex/imm-romania.git

# Instalează dependențe
pip3 install exchangelib requests requests_ntlm
```

## Configurare

### Input Files

Utilizatorul poate încărca fișiere de input în Nextcloud:

- **Folder pattern:** `Input from {owner_name}` unde `{owner_name}` este numele utilizatorului din USER.md
- **Locație:** `/{shared_folder}/Input from {owner_name}/`
- **Exemplu:** `/Alex's Assistant/Input from Alex/`
- Verificați acest folder când utilizatorul menționează fișiere încărcate

### Exchange

```bash
export EXCHANGE_SERVER="https://mail.your-domain.com/EWS/Exchange.asmx"
export EXCHANGE_USERNAME="service-account"
export EXCHANGE_PASSWORD="your-password"
export EXCHANGE_EMAIL="service-account@your-domain.com"
export EXCHANGE_VERIFY_SSL="false"  # pentru self-signed certs
```

### Nextcloud

```bash
export NEXTCLOUD_URL="https://cloud.your-domain.com"
export NEXTCLOUD_USERNAME="your-username"
export NEXTCLOUD_APP_PASSWORD="your-app-password"  # din Nextcloud > Settings > Security
```

### Memory (LCM Plugin)

```bash
openclaw plugins install @martian-engineering/lossless-claw
```

Vezi [references/setup.md](references/setup.md) pentru configurare completă.

## Utilizare

### Email

```bash
# Conexiune
imm-romania mail connect

# Listează
imm-romania mail read --limit 10 --unread

# Trimite
imm-romania mail send --to "client@ex.com" --subject "Ofertă" --body "Mesaj"
```

### Calendar

```bash
# Azi
imm-romania cal today

# Creează
imm-romania cal create --subject "Meeting" --start "2024-01-15 14:00" --duration 60
```

### Tasks

```bash
# Listează
imm-romania tasks list --overdue

# Creează
imm-romania tasks create --subject "Follow-up" --due "+7d" --priority high

# Completează
imm-romania tasks complete --id TASK_ID
```

### Fișiere

```bash
# Listează
imm-romania files list /Documents/

# Upload
imm-romania files upload /local/report.pdf /Documents/

# Download
imm-romania files download /Documents/report.pdf /local/
```

### Workflow-uri Combinate

```bash
# Download din Nextcloud și trimite pe email
imm-romania files download /Documents/offer.pdf /tmp/
imm-romania mail send --to "client@example.com" --subject "Ofertă" --attach /tmp/offer.pdf

# Creează task din email (manual, bazat pe conținut)
# LCM memorează contextul pentru referință ulterioară
```

## Structură

```
imm-romania/
├── SKILL.md              # Documentație OpenClaw (meta-skill)
├── README.md             # Acest fișier
├── LICENSE               # MIT License
├── CHANGELOG.md          # Istoric schimbări
├── requirements.txt      # Dependențe Python
├── config.template.yaml  # Template configurație
├── modules/
│   ├── exchange/          # Email, Calendar, Tasks
│   │   ├── SKILL.md
│   │   ├── mail.py
│   │   ├── cal.py
│   │   ├── tasks.py
│   │   └── sync.py
│   └── nextcloud/         # Fișiere
│       ├── SKILL.md
│       └── nextcloud.py
├── references/
│   └── setup.md          # Ghid instalare detaliat
├── assets/
│   └── config.template.yaml
├── scripts/
│   ├── imm-romania.py    # Orchestrator CLI
│   └── tests/
└── tests/
    └── test_all.py
```

## Testare

```bash
# Rulează toate testele
python3 -m pytest tests/

# Teste specifice
python3 -m pytest tests/test_all.py -v -k "mail"
python3 -m pytest tests/test_all.py -v -k "calendar"
python3 -m pytest tests/test_all.py -v -k "tasks"
```

## Troubleshooting

### Exchange SSL Error

```bash
export EXCHANGE_VERIFY_SSL="false"
```

### Exchange Authentication Failed

1. Verifică username (încearcă `DOMAIN\username` sau doar `username`)
2. Verifică password
3. Verifică că utilizatorul are mailbox

### Nextcloud 401 Unauthorized

1. Generează app password din Nextcloud > Settings > Security
2. Nu folosi password-ul principal

### Module Import Error

```bash
cd ~/.openclaw/skills/imm-romania
python3 -m modules.exchange mail connect
```

## Limitări

- Tasks sunt create în inbox-ul asistentului (EWS nu suportă task assignment)
- Pentru task-uri collaborative, folosiți calendar events
- Self-signed certificates necesită `verify_ssl: false`

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development standards and PR process.

This project follows the [Hardshell Coding Standards](https://github.com/assistentalex/openclaw-hardshell).

## Licență

MIT License - vezi [LICENSE](LICENSE)

## Autori

- Dezvoltat pentru comunitatea OpenClaw
- Publicat pe ClawHub
- Repository: https://github.com/assistentalex/openclaw-imm-romania

## Suport

- GitHub Issues: https://github.com/assistentalex/openclaw-imm-romania/issues
- Discord: [OpenClaw Community](https://discord.com/invite/clawd)