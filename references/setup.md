# IMM-Romania Setup Guide

Ghid complet de instalare și configurare pentru IMM-Romania skill.

## Cuprins

1. [Cerințe de Sistem](#cerințe-de-sistem)
2. [Instalare](#instalare)
3. [Configurare Exchange](#configurare-exchange)
4. [Configurare Nextcloud](#configurare-nextcloud)
5. [Configurare Memory (LCM)](#configurare-memory-lcm)
6. [Verificare Instalare](#verificare-instalare)
7. [Troubleshooting](#troubleshooting)

## Cerințe de Sistem

- Python 3.8+
- OpenClaw instalat și configurat
- Exchange Server 2016/2019 (on-premises)
- Nextcloud instance (optional)
- Conexiune la serverele respective

### Dependențe Python

```bash
pip install exchangelib requests requests_ntlm
```

## Instalare

### 1. Instalare Skill

```bash
# Copiază skill-ul în directorul OpenClaw
cp -r imm-romania ~/.openclaw/skills/

# Sau din sursă
cd ~/.openclaw/skills/
git clone https://github.com/your-org/imm-romania.git
```

### 2. Instalare Dependențe

```bash
cd ~/.openclaw/skills/imm-romania
pip install -r requirements.txt
```

## Configurare Exchange

### Opțiunea 1: Variabile de Mediu

```bash
# Adaugă în ~/.bashrc sau ~/.zshrc
export EXCHANGE_SERVER="https://mail.your-domain.com/EWS/Exchange.asmx"
export EXCHANGE_USERNAME="service-account"
export EXCHANGE_PASSWORD="your-password"
export EXCHANGE_EMAIL="service-account@your-domain.com"

# Pentru self-signed certificates
export EXCHANGE_VERIFY_SSL="false"
```

### Opțiunea 2: Fișier de Configurare

Creează `config.yaml` în directorul skill-ului:

```yaml
exchange:
  server: https://mail.your-domain.com/EWS/Exchange.asmx
  username: ${EXCHANGE_USERNAME}
  password: ${EXCHANGE_PASSWORD}
  email: service-account@your-domain.com
  verify_ssl: false
```

### Verificare Conexiune

```bash
python3 -m modules.exchange mail connect
```

Dacă conexiunea eșuează cu SSL error, verifică:
1. Certificate self-signed → setează `verify_ssl: false`
2. Porturi blocate → verifică firewall
3. Credențiale → verifică username/password

## Configurare Nextcloud

### 1. Generare App Password

1. Autentifică-te în Nextcloud
2. mergi la Settings → Security → Devices & sessions
3. Click "Create new app password"
4. Copiază password-ul generat

### 2. Variabile de Mediu

```bash
export NEXTCLOUD_URL="https://cloud.your-domain.com"
export NEXTCLOUD_USERNAME="your-username"
export NEXTCLOUD_APP_PASSWORD="your-app-password"
```

### 3. Verificare Conexiune

```bash
python3 -m modules.nextcloud list /
python3 -m modules.nextcloud list / --recursive
python3 -m modules.nextcloud search contract /Clients/
python3 -m modules.nextcloud summarize /Clients/contract.docx
python3 -m modules.nextcloud extract-actions /Clients/contract.txt
```

## Configurare Memory (LCM)

### Instalare Plugin

```bash
openclaw plugins install @martian-engineering/lossless-claw
```

### Configurare OpenClaw

Adaugă în `~/.openclaw/openclaw.json`:

```json
{
  "plugins": {
    "slots": {
      "contextEngine": "lossless-claw"
    },
    "entries": {
      "lossless-claw": {
        "enabled": true,
        "config": {
          "freshTailCount": 32,
          "contextThreshold": 0.75
        }
      }
    }
  }
}
```

### Verificare

LCM rulează automat. Verifică existența DB-ului:

```bash
ls -la ~/.openclaw/lcm.db
```

## Verificare Instalare

Rulează testele:

```bash
cd ~/.openclaw/skills/imm-romania
python3 -m pytest tests/
```

Sau manual:

```bash
# Test Exchange
python3 -m modules.exchange mail connect
python3 -m modules.exchange cal today

# Test Nextcloud
python3 -m modules.nextcloud list /
python3 -m modules.nextcloud search contract /Clients/
python3 -m modules.nextcloud extract-text /Clients/contract.docx
python3 -m modules.nextcloud summarize /Clients/contract.docx
python3 -m modules.nextcloud ask-file /Clients/contract.docx "When is the renewal due?"
python3 -m modules.nextcloud extract-actions /Clients/contract.txt
python3 -m modules.nextcloud create-tasks-from-file /Clients/contract.txt --dry-run
python3 -m modules.nextcloud share-list

# Test Tasks
python3 -m modules.exchange tasks list
```

## Troubleshooting

### Exchange SSL Error

```
Error: SSL: CERTIFICATE_VERIFY_FAILED
```

**Soluție**: Setează `verify_ssl: false` în config sau:

```bash
export EXCHANGE_VERIFY_SSL="false"
```

### Exchange Authentication Failed

```
Error: Unauthorized
```

**Verifică**:
1. Username corect (încearcă cu `DOMAIN\username` sau doar `username`)
2. Password corect
3. Contul are mailbox pe Exchange

### Nextcloud Connection Failed

```
Error: 401 Unauthorized
```

**Verifică**:
1. App password generat corect
2. URL corect (inclusiv https://)
3. 2FA este configurat corect

### LCM Not Working

**Verifică**:
1. Plugin instalat: `openclaw plugins list`
2. DB există: `ls ~/.openclaw/lcm.db`
3. Config corect: `openclaw plugins show lossless-claw`

### Module Import Error

```
ModuleNotFoundError: No module named 'modules.exchange'
```

**Soluție**: Rulează din rădăcina skill-ului:

```bash
cd ~/.openclaw/skills/imm-romania
python3 -m modules.exchange mail connect
```

## Configurație Completă Exemplu

```yaml
# ~/.openclaw/skills/imm-romania/config.yaml

exchange:
  server: https://mail.your-domain.com/EWS/Exchange.asmx
  username: service-account
  password: ${EXCHANGE_PASSWORD}
  email: service-account@your-domain.com
  verify_ssl: false

nextcloud:
  url: https://cloud.your-domain.com
  username: your-username
  app_password: ${NEXTCLOUD_APP_PASSWORD}

# LCM se configurează în openclaw.json
```

```bash
# ~/.bashrc sau ~/.zshrc

# Exchange
export EXCHANGE_SERVER="https://mail.your-domain.com/EWS/Exchange.asmx"
export EXCHANGE_USERNAME="service-account"
export EXCHANGE_PASSWORD="your-password"
export EXCHANGE_EMAIL="service-account@your-domain.com"
export EXCHANGE_VERIFY_SSL="false"

# Nextcloud
export NEXTCLOUD_URL="https://cloud.your-domain.com"
export NEXTCLOUD_USERNAME="your-username"
export NEXTCLOUD_APP_PASSWORD="your-app-password"
```