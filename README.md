<div align="center">

# OpenClaw-IMM-Romania

**Exchange, Nextcloud, GitHub — one assistant. Built by [Firma de AI](https://firmade.ai), supported by [Firma de IT](https://firmade.it)**

[![Version](https://img.shields.io/badge/version-0.3.0-blue.svg)](https://github.com/assistentalex/openclaw-imm-romania)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![OpenClaw Skill](https://img.shields.io/badge/OpenClaw-Skill-green.svg)](https://clawhub.ai)
[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-brightgreen.svg)](https://www.python.org/)
[![Firma de AI](https://img.shields.io/badge/built%20by-Firma%20de%20AI-6366f1.svg)](https://firmade.ai)
[![Firma de IT](https://img.shields.io/badge/supported%20by-Firma%20de%20IT-0ea5e9.svg)](https://firmade.it)

</div>

---

## Ce rezolvă acest skill OpenClaw?

Ai un mic business în România? Folosești Exchange și Nextcloud? 

Conectează Exchange și Nextcloud la OpenClaw. Citești și trimiți emailuri, programezi întâlniri, gestionezi task-uri și operezi fișiere pe Nextcloud — totul din terminal sau chat, fără interfață grafică.

## ⚡ Instalare rapidă în 3 pași

```bash
clawhub install imm-romania
imm-romania exchange connect    # configurează Exchange
imm-romania nextcloud connect   # configurează Nextcloud
imm-romania exchange mail list  # gata, funcționează
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

### 🐙 MSP GitHub Checker — Optional

Monitorizează release-uri publicate pentru repo-uri configurate și generează digest-uri utile pentru workflow-uri MSP.

```bash
imm-romania msp github-check repos
imm-romania msp github-check check --repo openclaw/openclaw --repo Martian-Engineering/lossless-claw
imm-romania msp github-check digest --check
```

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

## 🧰 Ecosistem

Skill-uri din aceeași familie, construite sub umbrela [Firma de AI](https://firmade.ai) și [Firma de IT](https://firmade.it):

| Skill | Ce face | Link |
|-------|----------|------|
| **Hardshell** | Coding standards pentru OpenClaw skills — PEP 8, type hints, testing, git workflow. Referință obligatorie pentru codul din acest proiect. | [openclaw-hardshell](https://github.com/assistentalex/openclaw-hardshell) |
| **prompt-to-pr** | Workflow complet de la prompt la PR gata de merge. 6 moduri (feature, fix, review, refactor, test, docs), token tracking, context budget, repo registry. | [openclaw-prompt-to-pr](https://github.com/assistentalex/openclaw-prompt-to-pr) |

---

## 🗺️ Roadmap

- [x] Exchange Email (read, send, draft, search)
- [x] Exchange Calendar (list, create, today, week)
- [x] Exchange Tasks (CRUD + delegat)
- [x] Nextcloud Files (upload, download, organize)
- [x] MSP Client Management
- [x] Optional GitHub Releases Checker (MSP-scoped)
- [ ] Exchange Contacts
- [ ] Email Templates
- [ ] Calendar Scheduling (find free slots)
- [ ] Multi-language support (RO/EN)

## 📄 Licență

MIT — vezi [LICENSE](LICENSE). Codul urmează [Hardshell Coding Standards](https://github.com/assistentalex/openclaw-hardshell).

---

<div align="center">

**[Built by Firma de AI](https://firmade.ai) · [Supported by Firma de IT](https://firmade.it) · Made with ☕ in România**

[Hardshell](https://github.com/assistentalex/openclaw-hardshell) · [prompt-to-pr](https://github.com/assistentalex/openclaw-prompt-to-pr) · [Report Bug](https://github.com/assistentalex/openclaw-imm-romania/issues) · [Request Feature](https://github.com/assistentalex/openclaw-imm-romania/issues)

</div>