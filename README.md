# T3rmx UserBot

**T3rmx UserBot** is an independent, modular Telegram automation framework built with Python, designed for extensibility, reliability, security, and advanced Telegram MTProto interactions.

> **Owner:** [@vvsks](https://t.me/vvsks) (`6023224495`)  
> **Repository:** <https://github.com/T3rmx/T3rmx-UserBot>  
> **Assistant bot:** [@t3rmx_official_bot](https://t.me/t3rmx_official_bot)  
> **Updates:** <https://t.me/t3rmx_official>  
> **Support:** <https://t.me/+3tqPFLpxCgVjZGVk> · <https://t.me/+ByL7rwqxpEEwOTE8>

<p align="center"><img src="assets/branding/t3rmx-logo.jpg" alt="T3rmx UserBot" width="420"></p>

## Overview
T3rmx UserBot is a Telethon-based userbot with an assistant bot, a large plugin surface, and modular deployment support. This repository is a standalone, in-repo distribution: application code, deployment assets, and the T3rmx-VC integration layer are maintained together.

## Features
- Telegram MTProto user automation (Telethon) with assistant bot and inline/help surfaces
- Extensive plugin system (administration, utilities, media, customization, and more)
- Backward-compatible environment configuration and legacy command/plugin compatibility where feasible
- Centralized owner authorization and safer runtime defaults (no auto-updates, no runtime code fetching)
- In-repo deployment targets: Heroku, Railway, Docker/Compose, VPS/systemd, direct Linux
- Independent `T3rmx-VC` adapter for voice-chat integration (verified call-control backend not bundled by default)

See [docs/audit/FEATURE_INVENTORY.md](docs/audit/FEATURE_INVENTORY.md) for the preserved feature inventory and [docs/architecture/T3RMX_VC.md](docs/architecture/T3RMX_VC.md) for VC status.

## Quick start

### Requirements
- Python 3.11+ recommended
- Telegram `APP_ID` / `API_HASH` (<https://my.telegram.org>)
- Telethon `STRING_SESSION`
- Assistant bot `TG_BOT_TOKEN` and `TG_BOT_USERNAME` (@BotFather)
- `ffmpeg` recommended for media features

### Run locally (Linux)
```bash
git clone https://github.com/T3rmx/T3rmx-UserBot.git
cd T3rmx-UserBot
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env with required values, then:
set -a; source .env; set +a
python3 -m JoKeRUB
```

Defaults: `TZ=Asia/Aden`, `ENV=production`. `TG_BOT_USERNAME` can be provided with or without `@`.

## Deployment
- [Heroku](docs/deployment/HEROKU.md)
- [Railway](docs/deployment/RAILWAY.md) (`railway.json` included; external template publication link documented separately if created)
- [Docker / Docker Compose](docs/deployment/DOCKER.md)
- [VPS / Linux / systemd](docs/deployment/VPS_LINUX.md)

## Configuration
Key variables (backward-compatible names preserved):

| Variable | Required | Notes |
|---|:---:|---|
| `APP_ID`, `API_HASH` | Yes | Telegram API credentials |
| `STRING_SESSION` | Yes | User session string |
| `TG_BOT_TOKEN`, `TG_BOT_USERNAME` | Yes | Assistant bot credentials (`@` optional) |
| `ALIVE_NAME` | No | Display name (default: T3rmx UserBot) |
| `TZ` | No | Default: `Asia/Aden` |
| `ENV` | No | Default: `production` |
| `DATABASE_URL` | No | Recommended for persistence |
| `COMMAND_HAND_LER` | No | Default: `.` |
| `VCMODE`, `VC_SESSION` | No | VC integration hooks (backend-dependent) |

See [`.env.example`](.env.example) and [`sample_config.py`](sample_config.py).

## Security
- Owner/developer privileged actions are restricted to the configured T3rmx owner (`6023224495`) by default.
- No automatic in-app updates, no runtime `pip install`, and no unverified external code fetching by default.
- `تحديث` performs read-only GitHub Releases checks for `T3rmx/T3rmx-UserBot` and provides manual, reviewed update guidance.
- See [docs/audit/SECURITY_AUDIT.md](docs/audit/SECURITY_AUDIT.md) and [docs/development/README.md](docs/development/README.md).

## Documentation
- [Architecture](docs/architecture/ARCHITECTURE.md)
- [Development](docs/development/README.md)
- [Dependencies](docs/DEPENDENCIES.md)
- [Audit & migration](docs/audit/)

## Attribution & license
This project is derived from audited upstream Telegram userbot codebases (including Jepthon/CatUserBot lineage). It is distributed under the **GNU Affero General Public License v3.0**. See [LICENSE](LICENSE), [BRANDING.md](BRANDING.md), and [docs/audit/SOURCE_PROVENANCE.md](docs/audit/SOURCE_PROVENANCE.md).

**Disclaimer:** Use responsibly and in compliance with Telegram’s Terms of Service and applicable laws. You are responsible for your account, credentials, and deployment.
