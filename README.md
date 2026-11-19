# T3rmx UserBot

**T3rmx UserBot** is an independent, modular Telegram automation framework built with Python, designed for extensibility, reliability, security, and advanced Telegram MTProto interactions.

> **Repository:** <https://github.com/T3rmx/T3rmx-UserBot>  
> **Assistant bot:** [@t3rmx_official_bot](https://t.me/t3rmx_official_bot)  
> **Updates:** <https://t.me/t3rmx_official>  
> **Support:** <https://t.me/+3tqPFLpxCgVjZGVk> · <https://t.me/+ByL7rwqxpEEwOTE8>

<p align="center"><img src="assets/branding/t3rmx-logo.jpg" alt="T3rmx UserBot" width="420"></p>

## Overview

T3rmx UserBot is a Telethon-based Telegram userbot with an assistant bot, a large plugin surface, and modular deployment support. This repository is a standalone, in-repo distribution: application code, deployment assets, and the T3rmx-VC integration layer are maintained together.

When deployed as your own instance, **you** provide your own Telegram credentials, session, bot token, owner ID, and database. Each deployment is independent and should never share another user's credentials, session, or database.

## Features

- Telegram MTProto user automation (Telethon) with assistant bot and inline/help surfaces
- Extensive plugin system (administration, utilities, media, customization, and more)
- Backward-compatible environment configuration and legacy command/plugin compatibility where feasible
- Centralized owner authorization (privileged actions are restricted to the configured deployment owner)
- Safer runtime defaults (no automatic in-app updates, no runtime `pip install`, no unverified runtime code fetching by default)
- Deployment assets for Railway, Docker/Compose, VPS/systemd, and direct Linux
- Independent `T3rmx-VC` adapter layer for voice-chat integration (a verified call-control backend is not bundled by default)

See [docs/audit/FEATURE_INVENTORY.md](docs/audit/FEATURE_INVENTORY.md) and [docs/architecture/T3RMX_VC.md](docs/architecture/T3RMX_VC.md).

## Deploy on Railway

> **Public Railway template status:** A real, published Railway Marketplace template URL/button is **not** included here until it is actually created, published, and verified with independent fresh deployments. Do not use fabricated template links.

Once a verified public template is published, the official button will be added in this format:

```md
[![Deploy on Railway](https://railway.com/button.svg)](ACTUAL_PUBLIC_TEMPLATE_URL)
```

### Deployment prerequisites

- A Railway account
- Your own Telegram account credentials (not someone else's)
- Telegram **API ID** and **API hash** from <https://my.telegram.org>
- A Telethon **string session** generated for your own Telegram account
- A Telegram **bot token** and **bot username** from [@BotFather](https://t.me/BotFather)
- Your own Telegram **numeric user ID** (used as `T3RMX_OWNER_ID` for privileged commands)
- A **PostgreSQL** database for the deployment (each deployment must use its own independent database)

### Telegram API setup

1. Open <https://my.telegram.org> and sign in with your Telegram account.
2. Go to **API development tools**.
3. Create an application if needed.
4. Copy your **API ID** (`APP_ID`) and **API hash** (`API_HASH`).

Keep these values private. Do not share them in public chats, screenshots, GitHub issues, or commits.

### Session generation instructions

T3rmx UserBot requires a Telethon **string session** for the user account that will run the userbot.

- Generate the session **locally and securely** using a trusted Telethon session generator/script you review.
- Use your own `APP_ID`/`API_HASH` when generating the session.
- Enter the resulting `STRING_SESSION` only into your deployment's private environment variables/secrets.
- Never publish or paste your session string anywhere public.

> **Security warning:** A string session grants account access. Treat it like a password. If exposed, revoke/re-generate it immediately and secure your Telegram account.

### Environment variables

| Variable | Required | Default | Description |
|---|:---:|---|---|
| `STRING_SESSION` | Yes | — | Your Telethon string session |
| `APP_ID` | Yes | — | Telegram API ID (`API_ID` alias supported) |
| `API_HASH` | Yes | — | Telegram API hash |
| `TG_BOT_TOKEN` | Yes | — | Telegram bot token from @BotFather |
| `TG_BOT_USERNAME` | Yes | — | Assistant bot username (with or without `@`) |
| `T3RMX_OWNER_ID` | Yes | — | **Your** Telegram numeric user ID (deployment owner for privileged commands) |
| `DATABASE_URL` | Yes (hosted/Railway production) | — | PostgreSQL URL for this deployment's own database |
| `ALIVE_NAME` | No | `T3rmx UserBot` | Display name |
| `TZ` | No | `UTC` | Timezone |
| `ENV` | No | `production` | Runtime environment |
| `COMMAND_HAND_LER` | No | `.` | Primary command prefix |
| `SUDO_COMMAND_HAND_LER` | No | `،` | Sudo command prefix |
| `VCMODE` | No | `false` | VC integration intent (backend-dependent) |
| `VC_SESSION` | No | empty | Optional VC session |
| `API_ID` | No | — | Backward-compatible alias for `APP_ID` |
| `OWNER_ID` | No | — | Backward-compatible alias for `T3RMX_OWNER_ID` |

Notes:
- `TG_BOT_USERNAME` can be provided with or without `@`.
- In hosted/Railway deployments, `DATABASE_URL` must be a PostgreSQL URL for a persistent, deployment-owned database. Ephemeral SQLite fallback is disabled in hosted environments to prevent data loss.
- `T3RMX_OWNER_ID` must be set to **your own** Telegram ID. Do not use another person's owner ID.

### PostgreSQL configuration

- Provision a **separate PostgreSQL database/service for each deployment**.
- Set `DATABASE_URL` to that deployment's own PostgreSQL connection string/reference.
- On Railway, prefer a **reference variable** to the deployment's own Postgres service (for example, the service-provided database URL variable) so credentials stay managed by the platform.
- Do not reuse another deployment's database.
- Do not point a public/shared template deployment at a personal or production database.

The application normalizes `postgres://` URLs to `postgresql://` for SQLAlchemy compatibility and creates required tables on startup.

### First startup instructions

1. Deploy the application with all required variables and a PostgreSQL `DATABASE_URL`.
2. Wait for the container/build to finish and the service to start.
3. Confirm the service is healthy:
   - `GET /` should return HTTP `200`
   - `GET /health` should return HTTP `200`
4. Open Telegram and test with your configured owner account (e.g. `.help` / `.alive` as applicable).
5. Verify privileged commands work only for `T3RMX_OWNER_ID` and are denied for other users.

If startup fails, check logs for missing/invalid configuration or database connectivity errors (secrets are not printed).

### Troubleshooting

- **Missing required configuration:** ensure `APP_ID`/`API_ID`, `API_HASH`, `STRING_SESSION`, `TG_BOT_TOKEN`, `TG_BOT_USERNAME`, `T3RMX_OWNER_ID`, and `DATABASE_URL` are set correctly for the deployment.
- **Healthcheck failing:** confirm the app is running, port binding is healthy, and `/health` responds with `200`.
- **Database errors / startup abort in hosted env:** verify `DATABASE_URL` points to this deployment's own PostgreSQL instance and is reachable.
- **Bot/userbot not responding:** verify Telegram credentials/session/token are valid for this deployment, the session is not revoked, and the assistant bot username/token match.
- **Privileged commands denied:** confirm `T3RMX_OWNER_ID` is your correct Telegram numeric user ID.
- **Voice/call-control features unavailable:** `T3rmx-VC` adapter hooks exist, but a verified call-control backend is not bundled by default.

### Security warnings

- Never commit `.env` files, session strings, API hashes, bot tokens, or database URLs.
- Never share `STRING_SESSION`, `API_HASH`, `TG_BOT_TOKEN`, or `DATABASE_URL` publicly.
- Each deployer must use their **own** Telegram credentials and **own** `T3RMX_OWNER_ID`.
- Each deployment must use its **own** PostgreSQL database.
- Privileged/owner actions are restricted to the configured deployment owner; keep your account and session secure.
- Review code/plugins before enabling additional features; runtime auto-install and external code fetching are disabled by default.

### Frequently asked questions

**Can I reuse someone else's session, bot token, or database?**  
No. Each deployment must be fully independent and use its own credentials and database.

**Can I deploy without PostgreSQL on Railway?**  
Not for a durable production/template deployment. Hosted deployments require a PostgreSQL `DATABASE_URL`.

**Is `API_ID` supported instead of `APP_ID`?**  
Yes, `API_ID` is accepted as a backward-compatible alias.

**Does this include voice chat/music call control?**  
The repository includes the T3rmx-VC integration layer/adapter hooks, but a verified call-control backend is not bundled by default.

### License

Distributed under the **GNU Affero General Public License v3.0**. See [LICENSE](LICENSE).

### Support

- Updates: <https://t.me/t3rmx_official>
- Support: <https://t.me/+3tqPFLpxCgVjZGVk> · <https://t.me/+ByL7rwqxpEEwOTE8>
- Issues: use GitHub issues for non-sensitive bug reports only (never post credentials, sessions, or tokens)

## Local / other deployment options

- [Railway deployment notes](docs/deployment/RAILWAY.md)
- [Heroku](docs/deployment/HEROKU.md)
- [Docker / Docker Compose](docs/deployment/DOCKER.md)
- [VPS / Linux / systemd](docs/deployment/VPS_LINUX.md)

### Quick start (local Linux)

```bash
git clone https://github.com/T3rmx/T3rmx-UserBot.git
cd T3rmx-UserBot
python3 -m venv .venv
. .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# edit .env with your own values, then:
set -a; source .env; set +a
python3 -m JoKeRUB
```

## Documentation

- [Architecture](docs/architecture/ARCHITECTURE.md)
- [Development](docs/development/README.md)
- [Dependencies](docs/DEPENDENCIES.md)
- [Audit & migration](docs/audit/)

## Attribution

This project is derived from audited upstream Telegram userbot codebases (including Jepthon/CatUserBot lineage). See [BRANDING.md](BRANDING.md) and [docs/audit/SOURCE_PROVENANCE.md](docs/audit/SOURCE_PROVENANCE.md).

**Disclaimer:** Use responsibly and in compliance with Telegram’s Terms of Service and applicable laws. You are responsible for your account, credentials, and deployment.
