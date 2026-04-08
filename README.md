<div align="center">

# 🇷🇴 IMM-Romania

**Asistentul tău digital pentru business-ul din România**

Email · Calendar · Task-uri · Fișiere — totul din terminalul tău

[![Version](https://img.shields.io/badge/version-0.3.0-blue.svg)](https://github.com/assistentalex/openclaw-imm-romania)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-green.svg)](https://clawhub.ai)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-brightgreen.svg)](https://www.python.org/)

</div>

---

## Ce rezolvă acest skill OpenClaw?

Ai un mic business în România? Folosești Exchange și Nextcloud? 

IMM-Romania îți aduce **totul într-un singur loc** — direct din chat sau terminal. Citești emailuri, programezi întâlniri, gestionezi task-uri și accesezi fișiere — **fără să deschizi 5 tab-uri**.

## ⚡ În 30 de secunde

```bash
# Instalează
clawhub install imm-romania

# Configurează (o singură dată)
imm-romania exchange connect
imm-romania nextcloud connect

# Gata — folosește-l
imm-romania exchange mail list --limit 5
imm-romania exchange cal today
imm-romania exchange tasks list
imm-romania nextcloud files list
```

## 🧩 Module

### 📧 Exchange — Email, Calendar & Tasks

Conecțiune completă la Exchange on-premises (2016/2019) prin EWS.

| Ce poți face | Comandă |
|---|---|
| Citește emailuri | `mail list` · `mail read` · `mail get --id X` |
| Trimite email | `mail send --to x@y.com --subject "Salut"` |
| Calendar azi | `cal today` |
| Calendar săptămână | `cal week` |
| Creează task | `tasks create --subject "Facturi" --due 2026-04-15` |
| Listează task-uri | `tasks list` · `tasks list --mailbox coleg@firma.ro` |
| Marchează ca citit | `mail mark-all-read` |
| Statistici inbox | `analytics stats` |

> 💡 **Acces delegat** — Folosește `--mailbox` pentru a lucra cu mailbox-ul unui coleg (cu permisiuni Editor)

### 📁 Nextcloud — Fișiere & Partajări

Gestionează fișiere pe Nextcloud prin WebDAV + OCS API.

| Ce poți face | Comandă |
|---|---|
| Listează fișiere | `nextcloud files list /calea/catre/folder` |
| Upload fișier | `nextcloud files upload local.pdf /Documente/` |
| Download fișier | `nextcloud files download /Documente/raport.pdf` |
| Creează folder | `nextcloud files mkdir /Documente/Nou` |
| Partajări | `nextcloud share list` |

### 🧠 Memory — Context Persistent

Păstrează istoria conversațiilor între sesiuni prin LCM plugin. Nu configurezi nimic — funcționează automat.

## 🛠️ Configurare

<details>
<summary><b>Exchange</b></summary>

```bash
export EXCHANGE_SERVER="https://mail.firma.ro/EWS/Exchange.asmx"
export EXCHANGE_USERNAME="cont@firma.ro"
export EXCHANGE_PASSWORD="parola"
export EXCHANGE_EMAIL="cont@firma.ro"
# Pentru self-signed certs:
export EXCHANGE_VERIFY_SSL="false"
```

Sau rulează `imm-romania exchange connect` pentru configurare interactivă.

</details>

<details>
<summary><b>Nextcloud</b></summary>

```bash
export NEXTCLOUD_URL="https://cloud.firma.ro"
export NEXTCLOUD_USERNAME="utilizator"
export NEXTCLOUD_APP_PASSWORD="parola-app"  # Settings > Security > App Password
```

</details>

<details>
<summary><b>Instalare manuală (fără ClawHub)</b></summary>

```bash
cd ~/.openclaw/skills/
git clone https://github.com/assistentalex/openclaw-imm-romania.git
pip3 install exchangelib requests requests_ntlm
```

</details>

## 📸 Cum arată

```json
// 📋 tasks list
{
  "ok": true,
  "tasks": [
    {"subject": "Facturi aprilie", "status": "InProgress", "due": "2026-04-15"},
    {"subject": "Raport lunar", "status": "NotStarted", "due": "2026-04-30"}
  ]
}
```

```json
// 📅 cal today
{
  "ok": true,
  "events": [
    {"subject": "Întâlnire echipă", "start": "10:00", "end": "11:00", "location": "Sala A"},
    {"subject": "Call client", "start": "14:00", "end": "15:00", "location": "Online"}
  ]
}
```

```json
// 📧 mail list --limit 2
{
  "ok": true,
  "messages": [
    {"subject": "Re: Ofertă proiect", "sender": "client@firma.ro", "is_read": false},
    {"subject": "Factura #1234", "sender": "contabilitate@firma.ro", "is_read": true}
  ]
}
```

## 🗺️ Roadmap

- [x] Exchange Email (read, send, draft, search)
- [x] Exchange Calendar (list, create, today, week)
- [x] Exchange Tasks (CRUD + delegat)
- [x] Nextcloud Files (upload, download, organize)
- [x] MSP Client Management
- [ ] Exchange Contacts
- [ ] Email Templates
- [ ] Calendar Scheduling (find free slots)
- [ ] Multi-language support (RO/EN)

## 🤝 Contribuie

Pull requests sunt binevenite! Codul urmează [Hardshell Coding Standards](https://github.com/assistentalex/openclaw-hardshell).

```bash
# Fork → Branch → PR
git checkout -b feature/nume-feature
git commit -m "feat: ce adaugi"
git push origin feature/nume-feature
```

## 📄 Licență

MIT — vezi [LICENSE](LICENSE)

---

<div align="center">

**Făcut cu ☕ pentru comunitatea OpenClaw din România**

[Report Bug](https://github.com/assistentalex/openclaw-imm-romania/issues) · [Request Feature](https://github.com/assistentalex/openclaw-imm-romania/issues) · [Discord](https://discord.com/invite/clawd)

</div>
